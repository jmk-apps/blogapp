from flask import Blueprint, render_template, redirect, flash, request, url_for
from blogapp import db
from flask_login import login_required, current_user
from blogapp.models import Newsletter
from blogapp.newsletters.forms import NewsletterForm, UpdateNewsletterForm
from blogapp.newsletters.utils import (save_newsletter_file, admin_required, delete_newsletter_file,
                                       send_newsletter_email)
from datetime import datetime, timezone


newsletters = Blueprint('newsletters', __name__)


@newsletters.route('/newsletter/new', methods=['GET', 'POST'])
@admin_required
@login_required
def new_newsletter():
    form = NewsletterForm()
    if form.validate_on_submit():
        newsletter_fn = save_newsletter_file(form.newsletter_file.data)
        newsletter_new = Newsletter(
            subject=form.subject.data,
            message=form.message.data,
            author=current_user.username,
            date_created=datetime.now(timezone.utc),
            newsletter_file=newsletter_fn
        )
        db.session.add(newsletter_new)
        db.session.commit()
        flash("Your newsletter has been created!", "success")
        return redirect(url_for('newsletters.newsletter_home'))

    return render_template("create_edit_newsletter.html", form=form,
                           legend="New Newsletter", title="New Newsletter")


@newsletters.route('/newsletter/<int:newsletter_id>', methods=['GET', 'POST'])
@admin_required
@login_required
def newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    return render_template("newsletter.html", legend="Newsletter",
                           newsletter=newsletter, title="Newsletter")


@newsletters.route('/newsletter/<int:newsletter_id>/update', methods=['GET', 'POST'])
@admin_required
@login_required
def update_newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    form = UpdateNewsletterForm()
    if form.validate_on_submit():
        if form.newsletter_file.data:
            delete_newsletter_file(newsletter.newsletter_file)
            file_name = save_newsletter_file(form.newsletter_file.data)
            newsletter.newsletter_file = file_name
        newsletter.subject = form.subject.data
        newsletter.message = form.message.data
        db.session.commit()
        flash("Your newsletter has been updated!", "success")
        return redirect(url_for('newsletters.newsletter', newsletter_id=newsletter.id))
    elif request.method == 'GET':
        form.subject.data = newsletter.subject
        form.message.data = newsletter.message
    newsletter_fn = newsletter.newsletter_file

    return render_template("create_edit_newsletter.html", form=form, letter_id=newsletter.id,
                           newsletter_file=newsletter_fn, legend="Update Newsletter", title="Update Newsletter")


@newsletters.route('/newsletter/<int:newsletter_id>/delete', methods=['POST'])
@admin_required
@login_required
def delete_newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    delete_newsletter_file(newsletter.newsletter_file)
    db.session.delete(newsletter)
    db.session.commit()
    flash("Your newsletter has been deleted!", "success")
    return redirect(url_for("newsletters.newsletter_home"))


@newsletters.route('/newsletter/<int:newsletter_id>/email', methods=['POST'])
@admin_required
@login_required
def email_newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    email_sent = send_newsletter_email(newsletter)
    if email_sent:
        flash("Your newsletter has been emailed to all subscribers!", "success")
    else:
        flash("Your newsletter was not emailed. Please check the subscriber list!", "danger")
    return redirect(url_for("newsletters.newsletter_home"))


@newsletters.route('/newsletter', methods=['GET', 'POST'])
@admin_required
@login_required
def newsletter_home():
    page = request.args.get('page', 1, type=int)
    newsletters = db.paginate(db.select(Newsletter).order_by(Newsletter.date_created.desc()), page=page, per_page=12)
    return render_template("newsletter_list.html", newsletters=newsletters, title="newsletters Home")



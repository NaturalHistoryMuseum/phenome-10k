from flask import Blueprint, render_template, request, current_app
from flask_mail import Message
from flask_security import current_user

from ..extensions import mail, security

bp = Blueprint('user', __name__, template_folder='../templates/user')


@bp.route('/contribute', methods=['GET', 'POST'])
def contribute():
    if current_user.is_authenticated and request.method == 'POST':
        message = request.form.get('message')

        body = (
            current_user.name + ' would like to become a contributor to Phenome10k:\n\n'
        )
        html = (
            current_user.name
            + ' would like to become a contributor to Phenome10k:<br><br>'
        )

        if message:
            body += '"' + message + '"\n\n'
            html += '<blockquote>"' + message + '"</blockquote><br><br>'

        # profile_link = url_for('users', user_id=current_user.id, _external=True)
        profile_link = '#'
        # FIXME

        body += 'To approve their request, use the following link:\n' + profile_link
        html += '<a href="' + profile_link + '">Approve this request</a>'

        mail.send(
            Message(
                recipients=[current_app.config['ADMIN_EMAIL']],
                reply_to=(current_user.name, current_user.email),
                subject=current_user.name
                + ' has requested to become a Phenome10k contributor',
                body=body,
                html=html,
            )
        )
    return render_template('contribute.html', title='Contributing')


@bp.route('/profile')
@bp.route('/profile/<user_id>')
def profile(user_id=None):
    user = security.datastore.find_user(id=user_id) if user_id else current_user
    return render_template(
        'profile.html',
        title=user.name,
        user=user,
        change_password_form=security.change_password_form(),
    )

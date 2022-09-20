from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_mail import Message
from flask_security import logout_user, current_user

from ..extensions import db, mail
from ..models import User

bp = Blueprint('user', __name__, template_folder='../templates/user')


@bp.route('/contribute', methods=['GET', 'POST'])
def contribute():
    if current_user.is_authenticated and request.method == 'POST':
        message = request.form.get('message')

        body = current_user.name + ' would like to become a contributor to Phenome10k:\n\n'
        html = current_user.name + ' would like to become a contributor to Phenome10k:<br><br>'

        if message:
            body += '"' + message + '"\n\n'
            html += '<blockquote>"' + message + '"</blockquote><br><br>'

        # profile_link = url_for('users', user_id=current_user.id, _external=True)
        profile_link = '#'
        # FIXME

        body += ('To approve their request, use the following link:\n' + profile_link)
        html += '<a href="' + profile_link + '">Approve this request</a>'

        mail.send(Message(
            recipients=[current_app.config['ADMIN_EMAIL']],
            reply_to=(current_user.name, current_user.email),
            subject=current_user.name + ' has requested to become a Phenome10k contributor',
            body=body,
            html=html
        ))
    return render_template('contribute.html', title='Contributing')

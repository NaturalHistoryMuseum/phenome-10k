from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_user, logout_user
from flask_mail import Message
from werkzeug.urls import url_parse

from ..extensions import db, mail
from ..forms import LoginForm, RegistrationForm
from ..models import User

bp = Blueprint('user', __name__, template_folder='../templates/user')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(next=request.args.get('next'))
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_and_migrate_password(form.password.data):
            # db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = form.next.data
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home.index')
            return redirect(next_page)
        else:
            error = 'Invalid email and/or password'
    return render_template('login.html', title='Sign In', form=form, error=error)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = RegistrationForm()
    error = None

    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, country_code=form.country.data,
                    user_type=form.organisation.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered and may log in')
        return redirect(url_for('user.login'))
    return render_template('register.html', title='Register', form=form, error=error)


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

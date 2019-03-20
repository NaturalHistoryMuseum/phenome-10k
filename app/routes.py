from flask import request, render_template, redirect, url_for, flash
import sqlite3
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(next=request.args.get('next'))
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.checkAndMigratePassword(form.password.data):
          db.session.commit()
          login_user(user, remember=form.remember_me.data)
          next_page = form.next.data
          if not next_page or url_parse(next_page).netloc != '':
              next_page = url_for('index')
          return redirect(next_page)
        else:
          error = 'Invalid email and/or password'
    return render_template('login.html', title='Sign In', form=form, error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
      return redirect(url_for('index'))
    form = RegistrationForm()
    error = None

    if form.validate_on_submit():
      user = User(name = form.name.data, email=form.email.data, country_code=form.country.data, user_type=form.organisation.data)
      user.setPassword(form.password.data)
      db.session.add(user)
      db.session.commit()
      flash('You are now registered and may log in')
      return redirect(url_for('login'))
    return render_template('register.html', title='Sign In', form=form, error=error)

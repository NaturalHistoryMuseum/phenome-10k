from flask import request, render_template, redirect, flash, url_for
from argon2 import PasswordHasher
import sqlite3
from app import app
from app.forms import LoginForm

user = {'username': 'Paul'}

@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

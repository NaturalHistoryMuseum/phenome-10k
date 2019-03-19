from flask import request, render_template, redirect, flash, url_for
from argon2 import PasswordHasher
import sqlite3
from app import app
from app.forms import LoginForm

db = sqlite3.connect('db.db')
ph = PasswordHasher()

cursor = db.cursor()
cursor.execute('''
  CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT unique, password TEXT)
''')
db.commit()
cursor.close()

user = {'username': 'Paul'}

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST' and request.form['submit']:
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    cursor.execute('''INSERT INTO users(username, password) VALUES(?, ?)''', (request.form['username'], ph.hash(request.form['password'])))
    cursor.execute('''SELECT * FROM users''')
    rows = cursor.fetchall()
    print(rows)
    db.commit()
    cursor.close()
    pass
  return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

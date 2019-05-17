from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import logging
from logging.handlers import RotatingFileHandler
import os
import click

app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Phenome10k startup')

from app import models, routes, errors

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': models.User, 'Scan': models.Scan}

@app.cli.command()
@click.argument('password')
def set_admin_pw(password):
    user = models.User(
        id = 1,
        name = 'Administrator',
        email = 'admin',
        role = 'ADMIN'
    )

    user = db.session.merge(user)

    if(user.checkPassword(password)):
        db.session.commit()
        print('Password not changed')
        return

    user.setPassword(password)
    db.session.commit()

    print('Password changed')

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import click
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from .data.scan_store import ScanStore

scan_store = ScanStore(db)

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

from . import models, routes, errors
from .routes import task_queue


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': models.User, 'Scan': models.Scan}


@app.cli.command()
@click.argument('password')
def set_admin_pw(password):
    user = models.User(
        id=1,
        name='Administrator',
        email='admin',
        role='ADMIN'
    )

    user = db.session.merge(user)

    if user.check_password(password):
        db.session.commit()
        print('Password not changed')
        return

    user.set_password(password)
    db.session.commit()

    print('Password changed')


from .tasks.server import TaskExecutor

task_executor = TaskExecutor(models.Queue, scan_store)


@app.cli.command()
@click.argument('scan_slug')
def create_ctm(scan_slug):
    task_queue.create_ctm(scan_slug)


@app.cli.command()
def task_runner():
    task_executor.run()


@app.cli.command()
def task():
    res = task_executor.next()
    if res:
        print('task success')
    else:
        print('no task to run')
        sys.exit(69)

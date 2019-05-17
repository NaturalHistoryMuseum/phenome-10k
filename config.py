import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(basedir, '../.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'G}<Ci&XWqSqA/mF7ZCWI7JJ.:QuuZF'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RENDER_AS_BATCH = not os.environ.get('DATABASE_URL')
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.mailtrap.io'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 2525
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') or False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    DEFAULT_MAIL_SENDER = os.environ.get('DEFAULT_MAIL_SENDER') or 'no-reply@phenome10k.org'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'test@example.com'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/phenome10k.log'

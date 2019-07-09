import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'G}<Ci&XWqSqA/mF7ZCWI7JJ.:QuuZF'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('%', '%%') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RENDER_AS_BATCH = not os.environ.get('DATABASE_URL')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'no-reply@phenome10k.org'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'test@example.com'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/phenome10k.log'
    SERVER_NAME = os.environ.get('SERVER_NAME')
    UPLOAD_DIRECTORY = os.environ.get('UPLOAD_DIRECTORY') or os.path.abspath('uploads')
    MODEL_DIRECTORY = os.environ.get('MODEL_DIRECTORY') or os.path.abspath('uploads/models')

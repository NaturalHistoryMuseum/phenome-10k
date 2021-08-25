import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# Parent directory takes precedence, which makes things
# easier when running in vagrant.
load_dotenv(os.path.join(basedir, '../.env'))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'G}<Ci&XWqSqA/mF7ZCWI7JJ.:QuuZF'
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or
                               'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RENDER_AS_BATCH = not os.environ.get('DATABASE_URL')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'no-reply@phenome10k.org'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'test@example.com'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/phenome10k.log'
    SERVER_NAME = os.environ.get('SERVER_NAME') or None
    UPLOAD_DIRECTORY = os.environ.get('UPLOAD_DIRECTORY') or os.path.abspath('uploads')
    MODEL_DIRECTORY = os.environ.get('MODEL_DIRECTORY') or os.path.abspath('uploads/models')
    THUMB_DIRECTORY = os.environ.get('THUMB_DIRECTORY') or os.path.abspath('thumbnails')
    TMP_UPLOAD = os.environ.get('TMP_UPLOAD') or '/tmp/upload-'
    RPC_HOST = os.environ.get('RPC_HOST') or 'http://localhost:8080'


def get_celery_config():
    return dict(
        broker=os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672'),
        backend=os.environ.get('CELERY_RESULTS_BACKEND', 'redis://localhost:6379/0')
    )

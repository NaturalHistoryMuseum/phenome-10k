import os

from dotenv import load_dotenv

# the project root where common things like the static folder and node src are stored
basedir = os.environ.get('BASE_DIR', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

load_dotenv(os.environ.get('P10K_ENV', os.path.join(basedir, '.env')))


class Config(object):
    BASE_DIR = basedir
    STATIC_DIR = os.environ.get('STATIC_DIR', os.path.join(basedir, 'static'))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'G}<Ci&XWqSqA/mF7ZCWI7JJ.:QuuZF'
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or
                               'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RENDER_AS_BATCH = not os.environ.get('DATABASE_URL')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@phenome10k.org')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = os.environ.get('MAIL_PORT', 25)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'alycejenni@gmail.com'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/phenome10k.log'
    SERVER_NAME = os.environ.get('SERVER_NAME') or None
    UPLOAD_DIRECTORY = os.environ.get('UPLOAD_DIRECTORY') or os.path.abspath('uploads')
    MODEL_DIRECTORY = os.environ.get('MODEL_DIRECTORY') or os.path.abspath('uploads/models')
    THUMB_DIRECTORY = os.environ.get('THUMB_DIRECTORY') or os.path.abspath('thumbnails')
    TMP_UPLOAD = os.environ.get('TMP_UPLOAD') or '/tmp/upload-'
    RPC_HOST = os.environ.get('RPC_HOST') or 'http://localhost:8080'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULTS_BACKEND', 'redis://localhost:6379/0')
    SECURITY_PASSWORD_HASH = 'argon2'
    SECURITY_PASSWORD_SCHEMES = ['argon2']
    SECURITY_PASSWORD_SINGLE_HASH = ['argon2']
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    HCAPTCHA_ENABLED = not os.environ.get('FLASK_DEBUG', False)
    HCAPTCHA_SITE_KEY = os.environ.get('HCAPTCHA_SITE_KEY')
    HCAPTCHA_SECRET_KEY = os.environ.get('HCAPTCHA_SECRET_KEY')


def get_celery_config():
    return dict(
        broker_url=Config.CELERY_BROKER_URL,
        result_backend=Config.CELERY_RESULT_BACKEND
    )

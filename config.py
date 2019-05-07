import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'G}<Ci&XWqSqA/mF7ZCWI7JJ.:QuuZF'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RENDER_AS_BATCH = not os.environ.get('DATABASE_URL')
    MAIL_SERVER = 'smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    DEFAULT_MAIL_SENDER = 'no-reply@phenome10k.org'
    ADMIN_EMAIL = 'test@example.com'

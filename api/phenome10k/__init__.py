from flask import Flask
from phenome10k.config import Config, get_celery_config
from phenome10k.extensions import db, migrate, security, mail, scan_store, upload_store, ma, spec, captcha
from phenome10k.tasks import celery
from phenome10k.models import user_datastore
from phenome10k.forms import P10KLoginForm, P10KRegisterForm


def init(return_celery=False):
    app = Flask(__name__, static_folder=Config.STATIC_DIR)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    security.init_app(app, user_datastore, login_form=P10KLoginForm, register_form=P10KRegisterForm)
    captcha.init_app(app)
    mail.init_app(app)
    scan_store.init_app(db)
    upload_store.init_app(app)
    ma.init_app(app)
    config_celery(app)

    from phenome10k.routes import init_routes
    init_routes(app)

    from phenome10k.schemas import init_schemas
    init_schemas(spec)

    return celery if return_celery else app


def config_celery(app):
    celery.conf.update(**get_celery_config())

    # https://flask.palletsprojects.com/en/1.1.x/patterns/celery/
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.finalize()


def create_app():
    return init()


def create_celery():
    return init(return_celery=True)

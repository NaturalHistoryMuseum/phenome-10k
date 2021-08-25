from flask import Flask
from phenome10k.config import Config, get_celery_config
from phenome10k.extensions import db, migrate, login, mail, celery, scan_store, upload_store
from phenome10k.models import User, Scan


def create_app():
    app = Flask(__name__, static_folder='../../static')
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    celery.conf.update(**get_celery_config())
    scan_store.init_app(db)
    upload_store.init_app(app)

    from phenome10k.routes import init_routes
    init_routes(app)

    return app

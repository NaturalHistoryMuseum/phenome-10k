from celery import Celery
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .data.scan_store import ScanStore
from .data.tmp_upload_store import TmpUploadStore

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'user.login'
mail = Mail()
celery = Celery(__name__)
scan_store = ScanStore()
upload_store = TmpUploadStore()

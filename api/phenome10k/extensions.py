
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from .data.scan_store import ScanStore
from .data.tmp_upload_store import TmpUploadStore

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'user.login'
mail = Mail()
ma = Marshmallow()
spec = APISpec(
    title='Phenome10k Query API',
    version='0.0.1',
    openapi_version='3.1.0',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)

scan_store = ScanStore()
upload_store = TmpUploadStore()

from flask_security import LoginForm
from wtforms import (StringField)
from wtforms.validators import DataRequired


class P10KLoginForm(LoginForm):
    email = StringField('Email', validators=[DataRequired()])

    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        if not self.user.check_and_migrate_password(self.password.data):
            return False
        return True

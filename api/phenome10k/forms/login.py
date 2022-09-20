from flask_security import LoginForm
from ..extensions import security


class P10KLoginForm(LoginForm):
    def validate(self, **kwargs):
        if not super().validate(**kwargs):
            return False
        if not self.user.check_and_migrate_password(self.password.data):
            return False
        return True

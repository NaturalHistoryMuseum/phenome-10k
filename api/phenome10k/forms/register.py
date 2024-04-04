import json
import urllib.request

from flask_security import ConfirmRegisterForm
from phenome10k.extensions import captcha
from phenome10k.models import User
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, ValidationError

data = urllib.request.urlopen('http://country.io/names.json').read()
countries = sorted(list(json.loads(data).items()), key=lambda x: x[1])


class P10KRegisterForm(ConfirmRegisterForm):
    name = StringField('Name', validators=[DataRequired()])
    country = SelectField('Country', choices=countries)
    organisation = SelectField(
        'Organisation',
        choices=[
            ('Other', 'Other'),
            ('Researcher', 'Researcher'),
            ('University', 'University'),
            ('Museum', 'Museum'),
            ('Teacher', 'Teacher'),
            ('Student', 'Student'),
        ],
    )

    # Todo: Use input & datalist instead of country select field
    # Validate/resolve against https://restcountries.eu/#api-endpoints-name

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate(self, **kwargs):
        if not captcha.verify():
            return False
        return super(P10KRegisterForm, self).validate(**kwargs)

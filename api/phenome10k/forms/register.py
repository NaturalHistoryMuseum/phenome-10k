import json
import urllib.request

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, SelectField)
from wtforms.validators import DataRequired, Email, ValidationError

from phenome10k.models import User

data = urllib.request.urlopen('http://country.io/names.json').read()
countries = list(json.loads(data).items())


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    country = SelectField('Country', choices=countries)
    organisation = SelectField(
        'Organisation',
        choices=[
            ('Other', 'Other'),
            ('Researcher', 'Researcher'),
            ('University', 'University'),
            ('Museum', 'Museum'),
            ('Teacher', 'Teacher'),
            ('Student', 'Student')
        ]
    )
    submit = SubmitField('Sign up')

    # Todo: Use input & datalist instead of country select field
    # Validate/resolve against https://restcountries.eu/#api-endpoints-name

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
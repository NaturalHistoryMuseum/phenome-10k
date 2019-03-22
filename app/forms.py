from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf.file import FileRequired
import json, urllib.request
from app.models import User

data = urllib.request.urlopen("http://country.io/names.json").read()
countries = list(json.loads(data).items())

class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    next = HiddenField()

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

class ScanUploadForm(FlaskForm):
    # TODO: For new upload, add validators=[FileRequired()]
    file = FileField('Scan file')
    scientific_name = StringField('Scientific Name', validators=[DataRequired()])
    alt_name = StringField('Alternate Name')
    specimen_location = StringField('Specimen Location')
    specimen_id = StringField('Specimen ID')
    description = TextAreaField('Description')
    # TODO: Change save button to upload/create/edit depending on context
    submit = SubmitField('Save')

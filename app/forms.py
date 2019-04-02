from flask_wtf import FlaskForm
from wtforms import widgets, StringField, PasswordField, BooleanField, SubmitField, HiddenField, SelectField, FileField, TextAreaField, MultipleFileField, SelectMultipleField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
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
    file = FileField('Scan file')
    stills = MultipleFileField('Stills')
    scientific_name = StringField('Scientific Name')
    alt_name = StringField('Alternate Name')
    specimen_location = StringField('Specimen Location')
    specimen_id = StringField('Specimen ID')
    description = TextAreaField('Description')
    pub_query = StringField('Query')
    pub_search = SubmitField('Search')
    publications_search = SelectMultipleField('Publications', choices = [], coerce = int, widget=widgets.ListWidget(), option_widget=widgets.CheckboxInput())
    publications = SelectMultipleField('Publications', choices = [], coerce = int, widget=widgets.ListWidget(), option_widget=widgets.CheckboxInput())
    attachments = MultipleFileField('Add files', default = [])
    # TODO: Change save button to upload/create/edit depending on context
    submit = SubmitField('Save')

    def json_data(self):
        return {
            k: v for k, v in self.data.items() if not isinstance(self[k], FileField)
        }

class PublicationUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    pub_year = StringField('Year', validators=[DataRequired()])
    authors = StringField('Authors', validators=[DataRequired()])
    journal = StringField('Journal, Volume and Page', validators=[DataRequired()])
    abstract = TextAreaField('Abstract', validators=[DataRequired()])
    link = StringField('URL Link')
    # TODO: Validate pdf files only
    files = MultipleFileField('Add files', default = [])
    # TODO: Change save button to upload/create/edit depending on context
    submit = SubmitField('Save')

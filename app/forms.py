from flask_wtf import FlaskForm
from wtforms import widgets, StringField, PasswordField, BooleanField, SubmitField, HiddenField, SelectField, FileField, TextAreaField, MultipleFileField, SelectMultipleField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
import json, urllib.request
from app.models import User, Tag, Publication
from app import db, app

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
    scientific_name = StringField('Scientific Name', validators = [DataRequired()])
    alt_name = StringField('Alternate Name')
    specimen_location = StringField('Specimen Location')
    specimen_id = StringField('Specimen ID')
    specimen_url = StringField('Specimen URL')
    description = TextAreaField('Description')
    publications = SelectMultipleField('Publications', choices = [], coerce = lambda id: id if isinstance(id, Publication) else Publication.query.get(int(id)), widget=widgets.ListWidget(), option_widget=widgets.CheckboxInput())
    attachments = MultipleFileField('Add files', default = [])
    geologic_age = SelectMultipleField('Geologic Age', choices = [ (tag, tag) for tag in Tag.query.filter_by(category='geologic_age').all() ], coerce = lambda id: id if isinstance(id, Tag) else Tag.query.get(int(id)), widget=widgets.ListWidget(), option_widget=widgets.CheckboxInput(), validators=[DataRequired()])
    ontogenic_age = SelectMultipleField('Ontogenic Age', choices = [ (tag, tag) for tag in Tag.query.filter_by(category='ontogenic_age').all() ], coerce = lambda id: id if isinstance(id, Tag) else Tag.query.get(int(id)), widget=widgets.ListWidget(), option_widget=widgets.CheckboxInput(), validators=[DataRequired()])
    elements = SelectMultipleField('Elements', choices = [ (tag, tag) for tag in Tag.query.filter_by(category='elements').all() ], coerce = lambda id: id if isinstance(id, Tag) else Tag.query.get(int(id)), widget=widgets.ListWidget(), option_widget=widgets.CheckboxInput(), validators=[DataRequired()])
    gbif_id = StringField()
    published = BooleanField('Publish')
    submit = SubmitField('Save')

    def serialize(self):
        data = {
            k: {
                'data': None if isinstance(self[k], FileField) else [ datum.serialize() if isinstance(datum, db.Model) else datum for datum in v ] if isinstance(v, list) else v,
                'errors': self[k].errors,
                'choices': [ choice[0].serialize() if isinstance(choice[0], db.Model) else choice for choice in self[k].choices ] if isinstance(self[k], SelectMultipleField) else None
            } for k, v in self.data.items()
        }

        tagTree = Tag.tree()
        data['geologic_age']['choices'] = tagTree['geologic_age']
        data['ontogenic_age']['choices'] = tagTree['ontogenic_age']
        data['elements']['choices'] = tagTree['elements']

        return data

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

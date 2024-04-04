from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired


class PublicationUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    pub_year = StringField('Year', validators=[DataRequired()])
    authors = StringField('Authors', validators=[DataRequired()])
    journal = StringField('Journal, Volume and Page', validators=[DataRequired()])
    abstract = TextAreaField('Abstract', validators=[DataRequired()])
    link = StringField('URL Link')
    # TODO: Validate pdf files only
    files = MultipleFileField('Add files', default=[])

    # Return the json-serializable object representation of this form
    def serialize(self):
        return {
            k: {
                'data': None if isinstance(self[k], FileField) else v,
                'errors': self[k].errors,
            }
            for k, v in self.data.items()
        }

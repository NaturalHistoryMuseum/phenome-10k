from flask_wtf import FlaskForm
from wtforms import (
    widgets,
    StringField,
    BooleanField,
    SubmitField,
    FileField,
    TextAreaField,
    MultipleFileField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired

from ..extensions import db
from ..models import Tag, Publication


class ScanUploadForm(FlaskForm):
    file = FileField('Scan file')
    stills = MultipleFileField('Stills')
    scientific_name = StringField('Scientific Name', validators=[DataRequired()])
    alt_name = StringField('Alternate Name')
    specimen_location = StringField('Specimen Location')
    specimen_id = StringField('Specimen ID')
    specimen_url = StringField('Additional Media')
    description = TextAreaField('Description')
    publications = SelectMultipleField(
        'Publications',
        choices=[],
        coerce=lambda f: f
        if isinstance(f, Publication)
        else Publication.query.get(int(f)),
        widget=widgets.ListWidget(),
        option_widget=widgets.CheckboxInput(),
    )
    attachments = MultipleFileField('Add files', default=[])
    geologic_age = SelectMultipleField(
        'Geologic Age',
        choices=[],
        coerce=lambda f: f if isinstance(f, Tag) else Tag.query.get(int(f)),
        widget=widgets.ListWidget(),
        option_widget=widgets.CheckboxInput(),
        validators=[DataRequired()],
    )
    ontogenic_age = SelectMultipleField(
        'Ontogenetic Age',
        choices=[],
        coerce=lambda f: f if isinstance(f, Tag) else Tag.query.get(int(f)),
        widget=widgets.ListWidget(),
        option_widget=widgets.CheckboxInput(),
        validators=[DataRequired()],
    )
    elements = SelectMultipleField(
        'Elements',
        choices=[],
        coerce=lambda f: f if isinstance(f, Tag) else Tag.query.get(int(f)),
        widget=widgets.ListWidget(),
        option_widget=widgets.CheckboxInput(),
        validators=[DataRequired()],
    )
    gbif_species_id = StringField()
    gbif_occurrence_id = StringField()
    published = BooleanField('Publish')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(ScanUploadForm, self).__init__(*args, **kwargs)
        self.geologic_age.choices = [
            (tag, tag) for tag in Tag.query.filter_by(category='geologic_age').all()
        ]
        self.ontogenic_age.choices = [
            (tag, tag) for tag in Tag.query.filter_by(category='ontogenic_age').all()
        ]
        self.elements.choices = [
            (tag, tag) for tag in Tag.query.filter_by(category='elements').all()
        ]

    def serialize(self):
        serialized_data = {
            k: {
                'data': (
                    None
                    if isinstance(self[k], FileField)
                    else (
                        [
                            datum.serialize() if isinstance(datum, db.Model) else datum
                            for datum in v
                        ]
                        if isinstance(v, list)
                        else v
                    )
                ),
                'errors': self[k].errors,
                'choices': [
                    choice[0].serialize() if isinstance(choice[0], db.Model) else choice
                    for choice in self[k].choices
                ]
                if isinstance(self[k], SelectMultipleField)
                else None,
            }
            for k, v in self.data.items()
        }

        tag_tree = Tag.tree()
        for key in ('geologic_age', 'ontogenic_age', 'elements'):
            if key in tag_tree:
                serialized_data[key]['choices'] = tag_tree[key]

        return serialized_data

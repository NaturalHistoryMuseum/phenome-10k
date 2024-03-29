from marshmallow import fields
from flask_marshmallow.fields import AbsoluteURLFor

from ._fields import PublicList
from .response import get_search_schema
from ..extensions import ma
from ..models import Publication


class PublicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Publication

    scans = PublicList(fields.Nested('NestedScanSchema'))

    url = AbsoluteURLFor('publications.view', values={'pub_object': '<id>'})


class NestedPublicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Publication
        exclude = ['published']

    url = AbsoluteURLFor('publications.view', values={'pub_object': '<id>'})


PublicationSearchResponse = get_search_schema(PublicationSchema)

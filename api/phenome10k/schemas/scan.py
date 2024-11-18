from flask_marshmallow.fields import AbsoluteURLFor
from marshmallow import fields

from ..extensions import ma
from ..models import Scan
from ._fields import PublicList
from .response import get_search_schema


class ScanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Scan
        include_fk = True

    publications = PublicList(fields.Nested('NestedPublicationSchema'))
    attachments = fields.List(fields.Nested('AttachmentSchema'))
    url = AbsoluteURLFor('scan.view', values={'scan_object': '<url_slug>'})


class NestedScanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Scan
        include_fk = True
        exclude = ['published']

    attachments = fields.List(fields.Nested('AttachmentSchema'))
    url = AbsoluteURLFor('scan.view', values={'scan_object': '<url_slug>'})


ScanSearchResponse = get_search_schema(ScanSchema)

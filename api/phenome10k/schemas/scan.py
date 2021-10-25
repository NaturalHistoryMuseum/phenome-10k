from marshmallow import fields
from flask_marshmallow.fields import AbsoluteURLFor

from ._fields import PublicList
from .response import get_search_schema
from ..extensions import ma
from ..models import Scan


class ScanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Scan
        include_fk = True

    publications = PublicList(
        fields.Nested('PublicationSchema',
                      exclude=['scans', 'published']))
    attachments = fields.List(
        fields.Nested('AttachmentSchema')
    )
    url = AbsoluteURLFor('scan.view', values={'scan_object': '<url_slug>'})


ScanSearchResponse = get_search_schema(ScanSchema)

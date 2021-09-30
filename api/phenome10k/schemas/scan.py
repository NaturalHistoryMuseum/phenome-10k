from marshmallow import fields

from ._utils import PublicList
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

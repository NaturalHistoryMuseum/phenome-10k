from .file_attachment import AttachmentSchema
from .publication import (
    NestedPublicationSchema,
    PublicationSchema,
    PublicationSearchResponse,
)
from .response import get_search_schema
from .scan import NestedScanSchema, ScanSchema, ScanSearchResponse


def init_schemas(spec):
    spec.components.schema('ScanSearchResponse', schema=ScanSearchResponse)
    spec.components.schema(
        'PublicationSearchResponse', schema=PublicationSearchResponse
    )

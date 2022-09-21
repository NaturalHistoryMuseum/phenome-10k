from .scan import ScanSchema, NestedScanSchema, ScanSearchResponse
from .publication import PublicationSchema, NestedPublicationSchema, PublicationSearchResponse
from .file_attachment import AttachmentSchema
from .response import get_search_schema


def init_schemas(spec):
    spec.components.schema('ScanSearchResponse', schema=ScanSearchResponse)
    spec.components.schema('PublicationSearchResponse', schema=PublicationSearchResponse)

from dataclasses import dataclass, field

from marshmallow import fields, Schema


@dataclass
class QueryResponse:
    valid_query: bool
    query_success: bool
    error: str = None
    q: object = None
    exact: bool = False
    offset: int = 0
    queried_attributes: object = field(default_factory=object)
    count: int = 0
    records: list = field(default_factory=list)


def get_search_schema(schema):
    search_schema = Schema.from_dict({
        'valid_query': fields.Boolean(required=True),
        'query_success': fields.Boolean(required=True),
        'error': fields.String(),
        'q': fields.String(),
        'exact': fields.Boolean(),
        'offset': fields.Integer(),
        'queried_attributes': fields.Dict(),
        'count': fields.Integer(),
        'records': fields.List(fields.Nested(schema))
    })
    return search_schema

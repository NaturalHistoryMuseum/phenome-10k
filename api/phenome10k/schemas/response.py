from marshmallow import fields, Schema


class QueryResponse:
    def __init__(
        self,
        valid_query: bool,
        query_success: bool,
        error: str = None,
        q: object = None,
        exact: bool = False,
        offset: int = 0,
        queried_attributes: object = None,
        count: int = 0,
        records: list = None,
    ):
        self.valid_query = valid_query
        self.query_success = query_success
        self.error = error
        self.q = q
        self.exact = exact
        self.offset = offset
        self.queried_attributes = queried_attributes or {}
        self.count = count
        self.records = records or []


def get_search_schema(schema):
    search_schema = Schema.from_dict(
        {
            'valid_query': fields.Boolean(required=True),
            'query_success': fields.Boolean(required=True),
            'error': fields.String(),
            'q': fields.String(),
            'exact': fields.Boolean(),
            'offset': fields.Integer(),
            'queried_attributes': fields.Dict(),
            'count': fields.Integer(),
            'records': fields.List(fields.Nested(schema)),
        }
    )
    return search_schema

from flask import Blueprint, jsonify, request, render_template

from ._utils import Query
from ..extensions import spec
from ..models import Scan, Publication
from ..schemas import (
    ScanSchema,
    PublicationSchema,
    ScanSearchResponse,
    PublicationSearchResponse,
)

bp = Blueprint('query', __name__, url_prefix='/api/v1')


@bp.route('/openapi.json')
def docs():
    return jsonify(spec.to_dict())


@bp.route('/docs')
def docs_ui():
    return render_template('docs/redoc.html')


@bp.route('/scan/<scan:scan_id>')
def scan_by_id(scan_id):
    """
    Retrieve data for a specific scan using its ID or url slug.
    ---
    get:
        description: Get scan by ID
        parameters:
            - name: scan_id
              in: path
              description: ID or url slug of the scan
        responses:
            200:
                content:
                    application/json:
                        schema: ScanSchema
    """
    return ScanSchema().dump(scan_id)


@bp.route('/scan/search')
def scan_search():
    """
    Search for one or more scans.
    ---
    get:
        description: Search scans
        parameters:
            - name: q
              in: query
              description: free-text search with '*' wildcards
            - name: exact
              in: query
              description: find an exact match or return an error
            - name: offset
              in: query
              description: for pagination
            - in: query
              schema: ScanSchema
        responses:
            200:
                content:
                    application/json:
                        schema: ScanSearchResponse
    """
    results = Query(Scan).search(**request.args)
    return ScanSearchResponse().dump(results)


@bp.route('/pub/<publication:pub_id>')
def pub_by_id(pub_id):
    """
    Retrieve data for a specific publication using its ID.
    ---
    get:
        description: Get publication by ID
        parameters:
            - name: pub_id
              in: path
              description: ID of the publication
        responses:
            200:
                content:
                    application/json:
                        schema: PublicationSchema
    """
    return PublicationSchema().dump(pub_id)


@bp.route('/pub/search')
def pub_search():
    """
    Search for one or more publications.
    ---
    get:
        description: Search publications
        parameters:
            - name: q
              in: query
              description: free-text search with '*' wildcards
            - name: exact
              in: query
              description: find an exact match or return an error
            - name: offset
              in: query
              description: for pagination
            - in: query
              schema: PublicationSchema
        responses:
            200:
                content:
                    application/json:
                        schema: PublicationSearchResponse
    """
    results = Query(Publication).search(**request.args)
    return PublicationSearchResponse().dump(results)

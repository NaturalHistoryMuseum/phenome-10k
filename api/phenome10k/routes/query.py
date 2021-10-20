from flask import Blueprint, jsonify, request

from ._utils import Query
from ..models import Scan, Publication
from ..schemas import ScanSchema, PublicationSchema

bp = Blueprint('query', __name__, url_prefix='/api/v1')


@bp.route('/')
def docs():
    return jsonify({'endpoints': []})


@bp.route('/scan/<scan:scan_object>')
def scan_by_id(scan_object):
    return ScanSchema().dump(scan_object)


@bp.route('/scan/search')
def scan_search():
    results = Query(Scan, ScanSchema).search(**request.args)
    return jsonify(results)


@bp.route('/pub/<publication:pub_object>')
def pub_by_id(pub_object):
    return PublicationSchema().dump(pub_object)


@bp.route('/pub/search')
def pub_search():
    results = Query(Publication, PublicationSchema).search(**request.args)
    return jsonify(results)

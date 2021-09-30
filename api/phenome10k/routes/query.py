from flask import Blueprint, jsonify
from ..schemas import ScanSchema

bp = Blueprint('query', __name__, url_prefix='/api/v1')


@bp.route('/')
def docs():
    return jsonify({'endpoints': []})


@bp.route('/scan/<scan:scan_object>')
def scan_by_id(scan_object):
    return ScanSchema().dump(scan_object)

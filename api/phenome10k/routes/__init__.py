from ..extensions import spec
from . import admin, files, home, publications, query, scans, user
from ._utils import FileConverter, PublicationConverter, ScanConverter
from .errors import forbidden_error, internal_error, not_found_error


def init_routes(app):
    blueprints = [
        home.bp,
        user.bp,
        admin.bp,
        *scans.bps,
        *publications.bps,
        files.bp,
        query.bp,
    ]

    app.url_map.strict_slashes = False
    app.url_map.converters['scan'] = ScanConverter
    app.url_map.converters['publication'] = PublicationConverter
    app.url_map.converters['file'] = FileConverter

    @app.after_request
    def add_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    documented_routes = [
        'query.scan_by_id',
        'query.scan_search',
        'query.pub_by_id',
        'query.pub_search',
    ]
    with app.app_context():
        for rule in documented_routes:
            spec.path(view=app.view_functions[rule])

    app.register_error_handler(403, forbidden_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

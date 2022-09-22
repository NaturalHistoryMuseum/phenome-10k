import requests
from flask import url_for, request, jsonify, render_template, current_app, redirect
from flask_security import current_user
from sqlalchemy.exc import MultipleResultsFound
from werkzeug.exceptions import Forbidden
from werkzeug.routing import BaseConverter, ValidationError, PathConverter

from ..extensions import db
from ..models import Scan, Publication
from ..schemas.response import QueryResponse


def hide_scan_files(data):
    if not current_user.is_authenticated:
        login_url = url_for('security.login')
        data['source'] = login_url
        for pub in data['publications']:
            for file in pub['files']:
                file['file'] = login_url
    return data


def ensure_editable(item):
    """Throw Forbidden exception if the current user is not allowed to edit the given model """
    if not current_user.can_edit(item):
        raise Forbidden('You cannot edit this item as you are not the original author.')


class SlugConverter(BaseConverter):
    regex = r'[^/]+'
    model = None

    def to_python(self, slug):
        model = self.model.find_by_slug(slug)
        if model is None:
            raise ValidationError
        return model

    def to_url(self, value):
        try:
            slug = value.url_slug or value.id
        except AttributeError:
            slug = str(value)
        return BaseConverter.to_url(self, slug)


class ScanConverter(SlugConverter):
    model = Scan


class PublicationConverter(SlugConverter):
    model = Publication


# This is just a one-way converter, to turn a File object into a router path. Doesn't work the other way.
class FileConverter(PathConverter):
    def to_url(self, value):
        return PathConverter.to_url(self, value if isinstance(value, str) else value.location)


def render_vue(data, title, menu=None):
    # Ensure browser cache doesn't confuse html and json docs at the same url
    # response.headers['Vary'] = 'Content-Type'

    if request.accept_mimetypes.accept_html:
        return render_content(content=vue(data), title=title, menu=menu)
    return jsonify(data)


def render_content(content, title, menu=None):
    return render_template('base.html', content=content, title=title, menu=menu)


# This is for server-side rendering a view in vue
# pass the url path and an object to be provided as the defaultData property to the vue model
def vue(default_data=None):
    path = request.full_path
    return rpc_call('render', [path, default_data])


def rpc_call(method, data):
    return rpc(current_app.config['RPC_HOST'], method, data)


def rpc(url, method, params):
    payload = {
        'method': method,
        'params': params,
        'jsonrpc': '2.0',
        'id': 0,
    }
    response = requests.post(url, json=payload).json()
    if 'error' in response:
        raise Exception(response['error']['message'])
    return response['result']


def make_aliases(main_blueprint, *alias_blueprints):
    def catchall(path):
        correct_prefix = main_blueprint.url_prefix.rstrip('/')
        intended_path = path.strip('/')
        return redirect(correct_prefix + '/' + intended_path)

    for alias in alias_blueprints:
        alias.route('/', defaults={'path': ''})(catchall)
        alias.route('/<path:path>')(catchall)


class Query(object):
    def __init__(self, model):
        self.model = model
        self._columns = {c.name: c for c in self.model.__table__.c}

    def search(self, **kwargs):
        """
        Search a model on its attributes.
        Additional kwargs:
            - q
            - exact
            - offset
        """
        r = QueryResponse(valid_query=False, query_success=False)
        query_args = {k: v for k, v in kwargs.items() if k in self._columns}
        r.queried_attributes = query_args
        r.q = kwargs.get('q')
        r.exact = kwargs.get('exact', False)
        try:
            r.offset = int(kwargs.get('offset', 0))
        except ValueError:
            r.offset = 0
        query_filters = []
        for k, v in query_args.items():
            if isinstance(v, str) and '*' in v:
                query_filters.append(self._columns[k].like(v.replace('*', '%')))
            else:
                query_filters.append(self._columns[k] == v)
        if r.q:
            or_filters = []
            if isinstance(r.q, str) and '*' in r.q:
                q = r.q.replace('*', '%')
                for c in self._columns.values():
                    or_filters.append(c.like(q))
            else:
                for c in self._columns.values():
                    try:
                        v = c.type.python_type(r.q)
                        or_filters.append(c == v)
                    except:
                        continue
            query_filters.append(db.or_(*or_filters))
        query = self.model.query.filter(*query_filters)
        if r.exact:
            try:
                results = query.one_or_none()
            except MultipleResultsFound:
                r.valid_query = True
                r.error = 'Multiple results found'
                return r
            except:
                r.error = 'Invalid query'
                return r
            r.valid_query = True
            r.query_success = len(results) == 1
            r.count = len(results)
            r.records = results
            return r
        else:
            try:
                results = query.order_by(self.model.id).offset(r.offset).limit(20).all()
            except:
                r.error = 'Invalid query'
                return r
            r.valid_query = True
            r.query_success = len(results) > 0
            r.count = len(results)
            r.records = results
            return r

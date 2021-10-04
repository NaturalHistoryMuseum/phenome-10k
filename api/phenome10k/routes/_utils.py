from flask import url_for, request, jsonify, render_template, current_app, redirect
from flask_login import current_user
from werkzeug.exceptions import Forbidden
from werkzeug.routing import BaseConverter, ValidationError, PathConverter
import requests

from ..models import Scan, Publication


def hide_scan_files(data):
    if not current_user.is_authenticated:
        login_url = url_for('user.login')
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
        return BaseConverter.to_url(self, value.url_slug or value.id)


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

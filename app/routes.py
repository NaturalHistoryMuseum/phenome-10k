import io
import math
import os
from functools import wraps
from zipfile import ZipFile

from PIL import Image
from flask import request, render_template, redirect, url_for, flash, send_from_directory, jsonify, g, Response, \
  send_file, make_response
from flask.helpers import safe_join
from flask_login import current_user, login_user, login_required, logout_user
from flask_mail import Message
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound, BadRequest, Forbidden
from werkzeug.routing import ValidationError, BaseConverter, PathConverter
from werkzeug.urls import url_parse

from app import app, db, models, scanStore
from app import mail
from app import rpc
from app.forms import LoginForm, RegistrationForm, ScanUploadForm, PublicationUploadForm
from app.models import User, Scan, File, Publication, Tag, Taxonomy, Attachment, ScanAttachment, PublicationFile
from .data.scan_store import ScanException
from .data.slugs import generate_slug
from .data.tmp_upload_store import TmpUploadStore
from .tasks.client import TaskQueue

uploadStore = TmpUploadStore(app.config['TMP_UPLOAD'])
taskQueue = TaskQueue(models.Queue)


def hideScanFiles(data):
    if not current_user.is_authenticated:
        login = url_for('login')
        data['source'] = login
        for pub in data['publications']:
            for file in pub['files']:
                file['file'] = login
    return data


def ensureEditable(item):
    """ Throw Forbidden exception if the current user is not allowed to edit the given model """
    if not current_user.canEdit(item):
        raise Forbidden('You cannot edit this item as you are not the original author.')


class SlugConverter(BaseConverter):
    regex = r'[^/]+'
    model = None

    def to_python(self, slug):
        model = self.model.findBySlug(slug)
        if model == None:
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


app.url_map.converters['scan'] = ScanConverter
app.url_map.converters['publication'] = PublicationConverter
app.url_map.converters['file'] = FileConverter


@app.after_request
def add_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    return response


def requiresAdmin(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.isAdmin():
            return render_template('403.html', message='You must be an administrator to access this page.',
                                   menu='home'), 403
        return f(*args, **kwargs)

    return decorated_function


def requiresContributor(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.isContributor():
            return render_template('403.html', message='You must be a contributor to access this page.',
                                   menu='home'), 403
        return f(*args, **kwargs)

    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', menu='home')


@app.route('/models/<file:path>')
def send_models(path):
    """Url for downloading the source model file"""
    return send_from_directory(app.config['MODEL_DIRECTORY'], path)


@app.route('/uploads/<file:path>')
def send_uploads(path):
    """Route for downloading an uploaded file. Images may be resized using the `w` parameter to specify width"""
    width = request.args.get('w')

    if width == None:
        return send_from_directory(app.config['UPLOAD_DIRECTORY'], path)

    thumbnail_file = path + '-' + width + '.png'

    try:
        return send_from_directory(app.config['THUMB_DIRECTORY'], thumbnail_file)
    except NotFound:
        thumbnail_file = safe_join(app.config['THUMB_DIRECTORY'], thumbnail_file)

        try:
            width = int(width)
        except ValueError:
            raise BadRequest('Thumbnail width must be an integer number')

        if width < 1:
            raise BadRequest('Thumbnail width must be greater than zero')

        try:
            im = Image.open(safe_join(app.config['UPLOAD_DIRECTORY'], path))
        except FileNotFoundError:
            raise NotFound()
        except OSError:
            raise BadRequest()

        if (width >= im.width):
            return send_from_directory(app.config['UPLOAD_DIRECTORY'], path)

        try:
            os.makedirs(os.path.dirname(thumbnail_file))
        except FileExistsError:
            pass

        height = im.height * width / im.width
        im.thumbnail((width, height))
        byteIO = io.BytesIO()
        im.save(byteIO, format='PNG')
        im.save(thumbnail_file, format='PNG')
        return Response(byteIO.getvalue(), mimetype='image/png', direct_passthrough=True)


@app.route('/about/', methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='About', menu='about')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(next=request.args.get('next'))
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.checkAndMigratePassword(form.password.data):
            # db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = form.next.data
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            error = 'Invalid email and/or password'
    return render_template('login.html', title='Sign In', form=form, error=error, menu='home')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    error = None

    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data, country_code=form.country.data,
                    user_type=form.organisation.data)
        user.setPassword(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered and may log in')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, error=error, menu='home')


@app.route('/library/')
@app.route('/library/<int:page>/')
@app.route('/scans/')
@app.route('/scans/<int:page>/')
def library(page=1):
    per_page = 100
    sort = request.args.get('sort')
    ontogenic_age = request.args.getlist('ontogenic_age')
    geologic_age = request.args.getlist('geologic_age')
    elements = request.args.getlist('elements')
    taxonomy = request.args.getlist('taxonomy')
    mine = 'mine' in request.args.keys()
    search = request.args.get('q')

    scanConditions = [
        Scan.published
    ]

    if search:
        searchQuery = '%{0}%'.format(search)

        textSearch = db.or_(
            Scan.scientific_name.ilike(searchQuery),
            Scan.alt_name.ilike(searchQuery),
            Scan.specimen_id.ilike(searchQuery),
            Scan.specimen_location.ilike(searchQuery),
            Scan.description.ilike(searchQuery)
        )

        scanConditions.append(textSearch)

    for searchTags in [ontogenic_age, geologic_age, elements]:
        if len(searchTags) > 0:
            scanConditions.append(
                Scan.tags.any(
                    Tag.taxonomy.startswith(searchTags[0]) if len(searchTags) == 1 else db.or_(
                        *[Tag.taxonomy.startswith(term) for term in searchTags])
                )
            )

    if len(taxonomy) > 0:
        scanConditions.append(Scan.taxonomy.any(Taxonomy.id.in_(taxonomy)))

    if mine and current_user.is_authenticated:
        scanConditions.append(Scan.author_id == current_user.id)

    scanConditions = db.and_(*scanConditions)

    # This is annoying... if we're sorting by name it's just sort,
    # but if we're sorting by tag we need to group it all.
    # Put it under the `groups` key so the view knows it needs to render differently
    if (sort in ('geologic_age', 'ontogenic_age')):
        results = [(tag, tag.scans.filter(scanConditions).all()) for tag in Tag.query.filter_by(category=sort).all()]

        data = {
            'groups': [
                {
                    'group': tag.name,
                    'items': [
                        s.serialize(full=False) for s in scans
                    ]
                }
                for (tag, scans) in results if len(scans) > 0
            ]
        }
    else:
        query = Scan.scientific_name

        results = Scan.query.filter(scanConditions).order_by(query).paginate(page, per_page)

        data = {
            'scans': [s.serialize(full=False) for s in results.items],
            'page': page,
            'total_pages': math.ceil(results.total / per_page)
        }

    data['tags'] = Tag.tree()
    data['tags']['taxonomy'] = Taxonomy.tree()
    data['q'] = search
    data['showMine'] = current_user.is_authenticated and current_user.isContributor()

    out = render_vue(data, title='Scans', menu='library')

    return out


@app.route('/feed')
def feed():
    """ Generate the RSS feed """
    scans = Scan.query.filter(Scan.published).order_by(Scan.date_created)
    resp = make_response(render_template('rss.xml', scans=scans))
    resp.headers['Content-type'] = 'application/rss+xml'
    return resp


@app.route('/library/manage-uploads/', methods=['GET', 'POST'])
@app.route('/library/manage-uploads/page/<int:page>/', methods=['GET', 'POST'])
@app.route('/scans/manage-uploads/', methods=['GET', 'POST'])
@app.route('/scans/manage-uploads/page/<int:page>/', methods=['GET', 'POST'])
@requiresContributor
def manage_uploads(page=1):
    """View a list of uploads with publish, edit, delete actions"""

    # Process delete request
    if request.method == 'POST':
        scan_id = request.form.get('delete')
        scan = Scan.query.get(scan_id)
        ensureEditable(scan)
        db.session.delete(scan)
        db.session.commit()
        return redirect(request.full_path)

    # To publish, we have to submit to the ScanUploadForm endpoint,
    # which requires a CSRF token. Construct the form to generate one.
    ScanUploadForm()

    per_page = 50
    offset = (page - 1) * per_page

    startswith = request.args.get('char')
    search = request.args.get('q')

    query = Scan.query

    if search:
        searchQuery = '%{0}%'.format(search)

        query = query.filter(
            db.or_(
                Scan.scientific_name.ilike(searchQuery),
                Scan.alt_name.ilike(searchQuery),
                Scan.specimen_id.ilike(searchQuery),
                Scan.specimen_location.ilike(searchQuery),
                Scan.description.ilike(searchQuery)
            )
        )

    if (startswith):
        query = query.filter(Scan.scientific_name.startswith(startswith))
    scans = query.paginate(page, per_page)
    data = {
        'scans': [s.serialize() for s in scans.items if current_user.canEdit(s)],
        'page': page,
        'total_pages': math.ceil(scans.total / per_page),
        'csrf_token': g.csrf_token,
        'q': search
    }
    return render_vue(data, title='Manage Uploads', menu='library')


@app.route('/<scan:scan>/')
def scan(scan):
    if not scan.published and not (current_user.is_authenticated and current_user.canEdit(scan)):
        raise NotFound()
    data = hideScanFiles(scan.serialize())

    return render_vue(data, title=scan.scientific_name, menu='library')


@app.route('/stills/<int:id>/', methods=['DELETE'])
@login_required
def delete_still(id):
    """Url for deleting a still"""
    attachment = ScanAttachment.query.filter_by(attachment_id=id).first()
    return_to = url_for('library')

    if attachment:
        ensureEditable(attachment)
        return_to = url_for('edit_scan', scan=attachment.scan)
        db.session.delete(attachment)
        db.session.commit()

    # Use a 303 response to force browser to use GET for the next request
    return redirect(return_to, code=303)


@app.route('/<scan:scan>/stills/')
@login_required
def scan_stills(scan):
    """Return a zip file containing all of the stills attached to this scan"""
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for still in scan.attachments:
            zip_file.write(still.file.getAbsolutePath(), still.file.filename)

    zip_buffer.seek(0)
    filename = scan.url_slug + '_stills.zip'

    return send_file(zip_buffer, as_attachment=True, attachment_filename=filename)


@app.route('/scans/batch-upload/', methods=['GET', 'POST'])
@requiresContributor
def upload_multi():
    files = []
    if request.method == 'POST':
        files = list(map(lambda f: f.filename, request.files.getlist('source')))
        app.logger.warning(files)

    data = rpc_call('views.batchUpload', [{'inputName': 'source', 'files': files}])

    return render_content(
        data.get('content'),
        data.get('title'),
        data.get('menu')
    )


@app.route('/files/', methods=['POST'])
@requiresContributor
def create_tmp_upload_file():
    res = Response(status=201)
    res.headers['Location'] = '/files/' + uploadStore.create()
    return res


@app.route('/files/<id>', methods=['PATCH'])
@requiresContributor
def append_tmp_upload_file(id):
    uploadStore.append(id, request.get_data())
    return Response(status=200)


@app.route('/<scan:scan>/edit', methods=['GET', 'POST'])
@app.route('/library/create/', methods=['GET', 'POST'])
@app.route('/scans/create/', methods=['GET', 'POST'])
@requiresContributor
def edit_scan(scan=None):
    form = ScanUploadForm(obj=scan)

    if scan:
        ensureEditable(scan)

        if not form.geologic_age.data:
            form.geologic_age.data = scan.geologic_age

        if not form.ontogenic_age.data:
            form.ontogenic_age.data = scan.ontogenic_age

        if not form.elements.data:
            form.elements.data = scan.elements

    # Get the records for the currently selected publications
    pubs = Publication.query.filter(Publication.author_id == current_user.id).all()
    form.publications.choices = [(pub, pub.title) for pub in pubs]

    if request.method == 'POST':
        if scan == None:
            scan = scanStore.new(current_user.email)

        # Make sure whatever publications are selected pass validation
        form.publications.choices = [(pub, pub.title) for pub in form.publications.data]

        form_valid = True

        # If file data is a UUID string then it's been through the blob uploader, get actual file
        # Todo: move this to uploadStore
        if isinstance(form.file.data, str):
            parts = form.file.data.split('/')
            location = parts[0]
            filename = parts[1] if len(parts) > 1 else None

            f = open(uploadStore.getFilepath(location), 'rb')
            form.file.data = FileStorage(f, filename)

        try:
            url = scanStore.update(scan, form.file.data, form.data, form.attachments.data)
            if form.file.data != None:
                taskQueue.create_ctm(scan.id)

            if form.published.data and form.validate():
                scanStore.publish(url)

        except ScanException as error:
            form_valid = False
            form.errors.append(error.message)

        finally:
            # Close the underlying stream if it's a file
            if form.file.data != None:
                form.file.data.close()

        if form_valid and not request.args.get('noredirect'):
            return redirect(request.args.get('redirect') or url_for('scan', scan=scan))

    data = {
        'form': form.serialize(),
        'scan': scan.serialize() if scan else None,
        'csrf_token': g.csrf_token
    }

    return render_vue(data, title='Edit' if scan else 'Upload New', menu='library')


@app.route('/publications/create/', methods=['GET', 'POST'])
@app.route('/publication/<publication:publication>/edit', methods=['GET', 'POST'])
@requiresContributor
def edit_publication(publication=None):
    form = PublicationUploadForm(obj=publication)

    if publication:
        ensureEditable(publication)

    if form.validate_on_submit():
        if not publication:
            publication = Publication(
                author_id=current_user.id,
                url_slug=generate_slug(form.title.data)
            )
            db.session.add(publication)
        publication.title = form.title.data
        publication.pub_year = form.pub_year.data
        publication.authors = form.authors.data
        publication.journal = form.journal.data
        publication.link = form.link.data
        publication.abstract = form.abstract.data
        publication.published = True

        for file in form.files.data:
            if file == '':
                continue
            f = File.fromUpload(file)
            db.session.add(f)
            publication.files.append(
                Attachment(
                    file=f,
                    name=file.filename
                )
            )

        db.session.commit()

        return redirect(url_for('edit_publication', publication=publication))

    data = {
        'publication': publication.serialize() if publication else None,
        'form': form.serialize(),
        'csrf_token': g.csrf_token
    }

    return render_vue(data, title='Edit' if publication else 'Create', menu='publications')


@app.route('/remove-pub-file/<int:id>', methods=['DELETE'])
@requiresContributor
def delete_pub_file(id):
    """Url for deleting a file"""
    attachment = PublicationFile.query.filter_by(attachment_id=id).first()
    return_to = url_for('publications')

    if attachment:
        ensureEditable(attachment)
        return_to = url_for('edit_publication', publication=attachment.publication)
        db.session.delete(attachment)
        db.session.commit()

    # Use a 303 response to force browser to use GET for the next request
    return redirect(return_to, code=303)


@app.route('/publications/')
@app.route('/publications/page/<int:page>/')
def publications(page=1):
    per_page = 100

    search = request.args.get('q')
    mine = 'mine' in request.args.keys()

    if search:
        searchQuery = '%{0}%'.format(search)

        query = Publication.query.filter(
            db.or_(
                Publication.title.ilike(searchQuery),
                Publication.authors.ilike(searchQuery)
            )
        )
    else:
        query = Publication.query

    if mine and current_user.is_authenticated:
        query = query.filter(Publication.author_id == current_user.id)

    query = query.order_by(Publication.pub_year.desc())

    pubs = query.filter_by(published=True).paginate(page, per_page)

    data = {
        'publications': [pub.serialize() for pub in pubs.items],
        'page': page,
        'total_pages': math.ceil(pubs.total / per_page),
        'q': search
    }

    return render_vue(data, title='Publications', menu='publications')


@app.route('/publications/manage-publications/', methods=['GET', 'POST'])
@app.route('/publications/manage-publications/page/<int:page>/', methods=['GET', 'POST'])
@requiresContributor
def manage_publications(page=1):
    """View a list of publications with publish, edit, delete actions"""

    # Process delete request
    if request.method == 'POST':
        action = request.form.get('action')
        publication_id = request.form.get('id')
        if publication_id:
            publication = Publication.query.get(publication_id)
            ensureEditable(publication)

            if action == 'delete':
                db.session.delete(publication)
                db.session.commit()
            elif action == 'publish':
                publication.published = True
                db.session.commit()
            elif action == 'unpublish':
                publication.published = False
                db.session.commit()
        return redirect(request.full_path)

    per_page = 50
    offset = (page - 1) * per_page

    pub_year = request.args.get('pub_year')
    search = request.args.get('q')

    query = Publication.query

    if search:
        searchQuery = '%{0}%'.format(search)

        query = query.filter(
            db.or_(
                Publication.title.ilike(searchQuery),
                Publication.authors.ilike(searchQuery)
            )
        )
    if (pub_year):
        query = query.filter_by(pub_year=pub_year)
    publications = query.order_by(Publication.pub_year.desc()).paginate(page, per_page)
    data = {
        'publications': [pub.serialize() for pub in publications.items if current_user.canEdit(pub)],
        'page': page,
        'total_pages': math.ceil(publications.total / per_page),
        'years': [y[0] for y in
                  db.session.query(Publication.pub_year).order_by(Publication.pub_year.desc()).distinct().all()],
        'q': search
    }
    return render_vue(data, title='Manage Publications', menu='publications')


@app.route('/publication/<publication:publication>/')
def publication(publication):
    if not publication.published and not (current_user.is_authenticated and current_user.canEdit(publication)):
        raise NotFound()
    return render_vue(publication.serialize(), title=publication.title, menu='publications')


@app.route('/contribute/', methods=['GET', 'POST'])
def contribute():
    if current_user.is_authenticated and request.method == 'POST':
        message = request.form.get('message')

        body = current_user.name + ' would like to become a contributor to Phenome10k:\n\n'
        html = current_user.name + ' would like to become a contributor to Phenome10k:<br><br>'

        if message:
            body += '"' + message + '"\n\n'
            html += '<blockquote>"' + message + '"</blockquote><br><br>'

        profileLink = url_for('users', id=current_user.id, _external=True)

        body += (
                'To approve their request, use the following link:\n' + profileLink
        )
        html += '<a href="' + profileLink + '">Approve this request</a>'

        mail.send(Message(
            recipients=[app.config['ADMIN_EMAIL']],
            reply_to=(current_user.name, current_user.email),
            subject=current_user.name + ' has requested to become a Phenome10k contributor',
            body=body,
            html=html
        ))
    return render_template('contribute.html', title='Contributing', menu='home')


@app.route('/users', methods=['GET', 'POST'])
@requiresAdmin
def users():
    error = ''

    if request.method == 'POST':
        id = request.form.get('id')
        user = User.query.get(id)

        if user:
            # Todo: Validation and errors
            user.role = request.form.get('role')
            db.session.commit()
            return redirect(url_for('users'))
        else:
            error = 'No user was found for id ' + id

    query = User.query
    id = request.args.get('id')

    if id:
        query = query.filter_by(id=id)

    users = [user.serialize() for user in query.all()]
    data = {'users': users, 'error': error}

    return render_vue(data, title='Users', menu='users')


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
def vue(defaultData=None):
    path = request.full_path
    return rpc_call('render', [path, defaultData])


def rpc_call(method, data):
    return rpc.rpc(app.config['RPC_HOST'], method, data)

import math

from flask import Blueprint, request, redirect, url_for, g
from flask import current_app
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound

from ._decorators import requires_contributor
from ._utils import hide_scan_files, render_vue, ensure_editable, render_content, rpc_call, make_aliases
from ..data.scan_store import ScanException
from ..extensions import db, scan_store, upload_store
from ..forms import ScanUploadForm
from ..models import Publication, Scan, Tag, Taxonomy
from ..tasks import create_ctm

bp = Blueprint('scans', __name__, url_prefix='/scans')
aliases = [Blueprint('library', 'library', url_prefix='/library')]

# library and scans are just aliases
make_aliases(bp, *aliases)

# scan and scans are not aliases
single_scan = Blueprint('scan', 'scan', url_prefix='/<scan:scan_object>')

bps = [bp, *aliases, single_scan]  # convenient for import


@bp.route('/')
@bp.route('/<int:page>')
def library(page=1):
    per_page = 100
    sort = request.args.get('sort')
    ontogenic_age = request.args.getlist('ontogenic_age')
    geologic_age = request.args.getlist('geologic_age')
    elements = request.args.getlist('elements')
    taxonomy = request.args.getlist('taxonomy')
    mine = 'mine' in request.args.keys()
    search = request.args.get('q')

    scan_conditions = [
        Scan.published
    ]

    if search:
        search_query = '%{0}%'.format(search)

        text_search = db.or_(
            Scan.scientific_name.ilike(search_query),
            Scan.alt_name.ilike(search_query),
            Scan.specimen_id.ilike(search_query),
            Scan.specimen_location.ilike(search_query),
            Scan.description.ilike(search_query)
        )

        scan_conditions.append(text_search)

    for search_tags in [ontogenic_age, geologic_age, elements]:
        if len(search_tags) > 0:
            scan_conditions.append(
                Scan.tags.any(
                    Tag.taxonomy.startswith(search_tags[0]) if len(search_tags) == 1 else db.or_(
                        *[Tag.taxonomy.startswith(term) for term in search_tags])
                )
            )

    if len(taxonomy) > 0:
        scan_conditions.append(Scan.taxonomy.any(Taxonomy.id.in_(taxonomy)))

    if mine and current_user.is_authenticated:
        scan_conditions.append(Scan.author_id == current_user.id)

    scan_conditions = db.and_(*scan_conditions)

    # This is annoying... if we're sorting by name it's just sort,
    # but if we're sorting by tag we need to group it all.
    # Put it under the `groups` key so the view knows it needs to render differently
    if sort in ('geologic_age', 'ontogenic_age'):
        results = [(tag, tag.scans.filter(scan_conditions).all()) for tag in Tag.query.filter_by(category=sort).all()]

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

        results = Scan.query.filter(scan_conditions).order_by(query).paginate(page, per_page)

        data = {
            'scans': [s.serialize(full=False) for s in results.items],
            'page': page,
            'total_pages': math.ceil(results.total / per_page)
        }

    data['tags'] = Tag.tree()
    data['tags']['taxonomy'] = Taxonomy.tree()
    data['q'] = search
    data['showMine'] = current_user.is_authenticated and current_user.is_contributor()

    return render_vue(data, title='Scan Library')


@bp.route('/manage-uploads', methods=['GET', 'POST'])
@bp.route('/manage-uploads/page/<int:page>', methods=['GET', 'POST'])
@requires_contributor
def manage(page=1):
    """View a list of uploads with publish, edit, delete actions"""

    # Process delete request
    if request.method == 'POST':
        scan_id = request.form.get('delete')
        scan_object = Scan.query.get(scan_id)
        ensure_editable(scan_object)
        db.session.delete(scan_object)
        db.session.commit()
        return redirect(request.full_path)

    # To publish, we have to submit to the ScanUploadForm endpoint,
    # which requires a CSRF token. Construct the form to generate one.
    ScanUploadForm()

    per_page = 50

    startswith = request.args.get('char')
    search = request.args.get('q')

    query = Scan.query

    if search:
        search_query = '%{0}%'.format(search)

        query = query.filter(
            db.or_(
                Scan.scientific_name.ilike(search_query),
                Scan.alt_name.ilike(search_query),
                Scan.specimen_id.ilike(search_query),
                Scan.specimen_location.ilike(search_query),
                Scan.description.ilike(search_query)
            )
        )

    if startswith:
        query = query.filter(Scan.scientific_name.startswith(startswith))
    scans = query.paginate(page, per_page)
    data = {
        'scans': [s.serialize() for s in scans.items if current_user.can_edit(s)],
        'page': page,
        'total_pages': math.ceil(scans.total / per_page),
        'csrf_token': g.csrf_token,
        'q': search
    }
    return render_vue(data, title='Manage Uploads')


@single_scan.route('/')
def view(scan_object):
    if not scan_object.published and not (current_user.is_authenticated and current_user.can_edit(scan_object)):
        raise NotFound()
    data = hide_scan_files(scan_object.serialize())

    return render_vue(data, title=scan_object.scientific_name)


@bp.route('/create', endpoint='create', methods=['GET', 'POST'])
@single_scan.route('/edit', methods=['GET', 'POST'])
@requires_contributor
def edit(scan_object=None):
    form = ScanUploadForm(obj=scan_object)

    if scan_object:
        ensure_editable(scan_object)

        if not form.geologic_age.data:
            form.geologic_age.data = scan_object.geologic_age

        if not form.ontogenic_age.data:
            form.ontogenic_age.data = scan_object.ontogenic_age

        if not form.elements.data:
            form.elements.data = scan_object.elements

    # Get the records for the currently selected publications
    pubs = Publication.query.filter(Publication.author_id == current_user.id).all()
    form.publications.choices = [(pub, pub.title) for pub in pubs]

    if request.method == 'POST':
        if scan_object is None:
            scan_object = scan_store.new(current_user.email)

        # Make sure whatever publications are selected pass validation
        form.publications.choices = [(pub, pub.title) for pub in form.publications.data]

        form_valid = True

        # If file data is a UUID string then it's been through the blob uploader, get actual file
        # Todo: move this to uploadStore
        if isinstance(form.file.data, str):
            parts = form.file.data.split('/')
            location = parts[0]
            filename = parts[1] if len(parts) > 1 else None

            f = open(upload_store.get_filepath(location), 'rb')
            form.file.data = FileStorage(f, filename)

        try:
            url = scan_store.update(scan_object, form.file.data, form.data, form.attachments.data)
            if form.file.data is not None:
                create_ctm.delay(scan_object.id)

            if form.published.data and form.validate():
                scan_store.publish(url)

        except ScanException as error:
            form_valid = False
            form.errors.append(error.message)

        finally:
            # Close the underlying stream if it's a file
            if form.file.data is not None:
                form.file.data.close()

        if form_valid and not request.args.get('noredirect'):
            return redirect(request.args.get('redirect') or url_for('scan.view', scan_object=scan_object))

    data = {
        'form': form.serialize(),
        'scan': scan_object.serialize() if scan_object else None,
        'csrf_token': g.csrf_token
    }

    return render_vue(data, title='Edit' if scan_object else 'Upload New')


@single_scan.route('/stills')
@login_required
def stills(scan_object):
    """Deprecated route"""
    return redirect(url_for('files.get_stills', scan_object=scan_object))


@bp.route('/batch-upload', methods=['GET', 'POST'])
@requires_contributor
def upload_multi():
    files = []
    if request.method == 'POST':
        files = list(map(lambda f: f.filename, request.files.getlist('source')))
        current_app.logger.warning(files)

    data = rpc_call('views.batchUpload', [{'inputName': 'source', 'files': files}])

    return render_content(
        data.get('content'),
        data.get('title')
    )

import math

from flask import Blueprint, request, redirect, g, url_for
from flask_security import current_user
from werkzeug.exceptions import NotFound

from ._decorators import requires_contributor
from ._utils import ensure_editable, make_aliases, render_vue
from ..data.slugs import generate_slug
from ..extensions import db
from ..forms import PublicationUploadForm
from ..models import File, Publication, Attachment

bp = Blueprint('publications', __name__, url_prefix='/publications')
aliases = [Blueprint('publication', 'publication', url_prefix='/publication')]

bps = [bp, *aliases]

# may as well just combine /publication and /publications because they overlap
# and look way too similar
make_aliases(bp, *aliases)


@bp.route('/')
@bp.route('/page/<int:page>')
def library(page=1):
    per_page = 100

    search = request.args.get('q')
    mine = 'mine' in request.args.keys()

    if search:
        search_query = '%{0}%'.format(search)

        query = Publication.query.filter(
            db.or_(
                Publication.title.ilike(search_query),
                Publication.authors.ilike(search_query),
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
        'q': search,
        'showMine': current_user.is_authenticated and current_user.can_contribute(),
    }

    return render_vue(data, title='Publications')


@bp.route('/manage-publications', methods=['GET', 'POST'])
@bp.route('/manage-publications/page/<int:page>', methods=['GET', 'POST'])
@requires_contributor
def manage(page=1):
    """
    View a list of publications with publish, edit, delete actions.
    """

    # Process delete request
    if request.method == 'POST':
        action = request.form.get('action')
        publication_id = request.form.get('id')
        if publication_id:
            pub_object = Publication.query.get(publication_id)
            ensure_editable(pub_object)

            if action == 'delete':
                db.session.delete(pub_object)
                db.session.commit()
            elif action == 'publish':
                pub_object.published = True
                db.session.commit()
            elif action == 'unpublish':
                pub_object.published = False
                db.session.commit()
        return redirect(request.full_path)

    per_page = 50

    pub_year = request.args.get('pub_year')
    search = request.args.get('q')

    query = Publication.query

    if search:
        search_query = '%{0}%'.format(search)

        query = query.filter(
            db.or_(
                Publication.title.ilike(search_query),
                Publication.authors.ilike(search_query),
            )
        )
    if pub_year:
        query = query.filter_by(pub_year=pub_year)
    pub_list = query.order_by(Publication.pub_year.desc()).paginate(page, per_page)
    data = {
        'publications': [
            pub.serialize() for pub in pub_list.items if current_user.can_edit(pub)
        ],
        'page': page,
        'total_pages': math.ceil(pub_list.total / per_page),
        'years': [
            y[0]
            for y in db.session.query(Publication.pub_year)
            .order_by(Publication.pub_year.desc())
            .distinct()
            .all()
        ],
        'q': search,
    }
    return render_vue(data, title='Manage Publications')


@bp.route('/<publication:pub_object>/')
def view(pub_object):
    if not pub_object.published and not (
        current_user.is_authenticated and current_user.can_edit(pub_object)
    ):
        raise NotFound()
    return render_vue(pub_object.serialize(), title=pub_object.title)


@bp.route('/create', endpoint='create', methods=['GET', 'POST'])
@bp.route('/<publication:pub_object>/edit', methods=['GET', 'POST'])
@requires_contributor
def edit(pub_object=None):
    form = PublicationUploadForm(obj=pub_object)

    if pub_object:
        ensure_editable(pub_object)

    if form.validate_on_submit():
        if not pub_object:
            pub_object = Publication(
                author_id=current_user.id, url_slug=generate_slug(form.title.data)
            )
            db.session.add(pub_object)
        pub_object.title = form.title.data
        pub_object.pub_year = form.pub_year.data
        pub_object.authors = form.authors.data
        pub_object.journal = form.journal.data
        pub_object.link = form.link.data
        pub_object.abstract = form.abstract.data
        pub_object.published = True

        for file in form.files.data:
            if file == '' or file.filename == '':
                continue
            f = File.from_upload(file)
            db.session.add(f)
            pub_object.files.append(Attachment(file=f, name=file.filename))

        db.session.commit()

        return redirect(url_for('publications.view', pub_object=pub_object))

    data = {
        'publication': pub_object.serialize() if pub_object else None,
        'form': form.serialize(),
        'csrf_token': g.csrf_token,
    }

    return render_vue(data, title='Edit' if pub_object else 'Create')

from flask import Blueprint, request, redirect, url_for

from ..extensions import db
from ..models import User, user_datastore
from ._decorators import requires_admin
from ._utils import render_vue

bp = Blueprint('admin', __name__)


@bp.route('/users', methods=['GET', 'POST'])
@requires_admin
def users():
    error = ''

    if request.method == 'POST':
        user_id = request.form.get('id')
        user = User.query.get(user_id)

        if user:
            # Todo: Validation and errors
            role = user_datastore.find_role(request.form.get('role'))
            user_datastore.add_role_to_user(user, role)
            user_datastore.commit()
            return redirect(url_for('admin.users'))
        else:
            error = 'No user was found for id ' + user_id

    query = User.query
    user_columns = {c.name: getattr(User, c.name) for c in User.__table__.c}
    filters = []
    filter_dict = {}
    for filter_name, v in request.args.items():
        if filter_name not in user_columns or filter_name == 'password':
            continue
        filter_dict[filter_name] = v
        if '*' in v:
            v = v.replace('*', '%')
            filters.append(user_columns[filter_name].ilike(v))
        else:
            filters.append(user_columns[filter_name] == v)

    role_filter = request.args.get('role')
    if role_filter:
        filters.append(User.roles.any(name=role_filter))

    query = query.filter(*filters)

    try:
        limit = int(request.args.get('limit', 50))
    except:
        limit = 50

    try:
        offset = int(request.args.get('offset', 0))
    except:
        offset = 0

    users_list = [user.serialize() for user in query.limit(limit).offset(offset).all()]
    data = {'users': users_list, 'error': error, 'total': query.count(), 'pageSize': limit, 'offset': offset, 'filters': filter_dict}

    return render_vue(data, title='Users')

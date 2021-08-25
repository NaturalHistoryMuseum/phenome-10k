from flask import Blueprint, request, redirect, url_for

from ..extensions import db
from ..models import User
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
            user.role = request.form.get('role')
            db.session.commit()
            return redirect(url_for('admin.users'))
        else:
            error = 'No user was found for id ' + user_id

    query = User.query
    user_id = request.args.get('id')

    if user_id:
        query = query.filter_by(id=user_id)

    users_list = [user.serialize() for user in query.all()]
    data = {'users': users_list, 'error': error}

    return render_vue(data, title='Users')

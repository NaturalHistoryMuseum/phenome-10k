from flask import render_template

from ..extensions import db


def forbidden_error(error):
    return render_template('errors/403.html', message=error.description), 403


def not_found_error(error):
    return render_template('errors/404.html'), 404


def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

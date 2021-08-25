from flask import Blueprint, render_template, make_response

from ..models import Scan

bp = Blueprint('home', __name__, template_folder='../templates/home')


@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@bp.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='About')


@bp.route('/feed')
def feed():
    """ Generate the RSS feed """
    scans = Scan.query.filter(Scan.published).order_by(Scan.date_created)
    resp = make_response(render_template('rss.xml', scans=scans))
    resp.headers['Content-type'] = 'application/rss+xml'
    return resp

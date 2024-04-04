import io
import os
from zipfile import ZipFile

from PIL import Image
from flask import Blueprint, redirect, url_for, send_file
from flask import Response, current_app, send_from_directory
from flask import request
from flask.helpers import safe_join
from werkzeug.exceptions import NotFound, BadRequest

from ._decorators import login_required, requires_contributor
from ._utils import ensure_editable
from ..extensions import db, upload_store
from ..models import PublicationFile, ScanAttachment, Publication, Scan

bp = Blueprint('files', __name__, url_prefix='/files')


@bp.route('/', methods=['POST'])
@requires_contributor
def create_tmp_upload_file():
    res = Response(status=201)
    res.headers['Location'] = '/files/' + upload_store.create()
    return res


@bp.route('/<file_id>', methods=['PATCH'])
@requires_contributor
def append_tmp_upload_file(file_id):
    upload_store.append(file_id, request.get_data())
    return Response(status=200)


@bp.route('/pub/<int:attach_id>/delete', methods=['DELETE'])
@requires_contributor
def delete_pub_file(attach_id):
    """
    Url for deleting a file.
    """
    attachment = PublicationFile.query.filter_by(attachment_id=attach_id).first()
    return_to = url_for('publications.library')

    if attachment:
        ensure_editable(attachment)
        publication = Publication.query.get(attachment.publication_id)
        return_to = url_for('publications.edit', pub_object=publication)
        db.session.delete(attachment)
        db.session.commit()

    # Use a 303 response to force browser to use GET for the next request
    return redirect(return_to, code=303)


@bp.route('/models/<file:path>')
def send_models(path):
    """
    Url for downloading the source model file.
    """
    return send_from_directory(current_app.config['MODEL_DIRECTORY'], path)


@bp.route('/uploads/<file:path>')
def send_uploads(path):
    """
    Route for downloading an uploaded file.

    Images may be resized using the `w` parameter to specify width
    """
    width = request.args.get('w')

    if width is None:
        return send_from_directory(current_app.config['UPLOAD_DIRECTORY'], path)

    thumbnail_file = path + '-' + width + '.png'

    try:
        return send_from_directory(
            current_app.config['THUMB_DIRECTORY'], thumbnail_file
        )
    except NotFound:
        thumbnail_file = safe_join(
            current_app.config['THUMB_DIRECTORY'], thumbnail_file
        )

        try:
            width = int(width)
        except ValueError:
            raise BadRequest('Thumbnail width must be an integer number')

        if width < 1:
            raise BadRequest('Thumbnail width must be greater than zero')

        try:
            im = Image.open(safe_join(current_app.config['UPLOAD_DIRECTORY'], path))
        except FileNotFoundError:
            raise NotFound()
        except OSError:
            raise BadRequest()

        if width >= im.width:
            return send_from_directory(current_app.config['UPLOAD_DIRECTORY'], path)

        try:
            os.makedirs(os.path.dirname(thumbnail_file))
        except FileExistsError:
            pass

        height = im.height * width / im.width
        im.thumbnail((width, height))
        byte_io = io.BytesIO()
        im.save(byte_io, format='PNG')
        im.save(thumbnail_file, format='PNG')
        return Response(
            byte_io.getvalue(), mimetype='image/png', direct_passthrough=True
        )


@bp.route('/stills/<scan:scan_object>')
@login_required
def get_stills(scan_object):
    """
    Return a zip file containing all of the stills attached to this scan.
    """
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for still in scan_object.attachments:
            zip_file.write(still.file.get_absolute_path(), still.file.filename)

    zip_buffer.seek(0)
    filename = scan_object.url_slug + '_stills.zip'

    return send_file(zip_buffer, as_attachment=True, attachment_filename=filename)


@bp.route('/stills/<int:still_id>', methods=['DELETE'])
@login_required
def delete_still(still_id):
    """
    Url for deleting a still.
    """
    attachment = ScanAttachment.query.filter_by(attachment_id=still_id).first()
    return_to = url_for('scans.library')

    if attachment:
        ensure_editable(attachment)
        scan = Scan.query.get(attachment.scan_id)
        return_to = url_for('scan.edit', scan_object=scan)
        db.session.delete(attachment)
        db.session.commit()

    # Use a 303 response to force browser to use GET for the next request
    return redirect(return_to, code=303)

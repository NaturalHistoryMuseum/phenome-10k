import os
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from stl.mesh import Mesh
from werkzeug.utils import secure_filename

from .ctmconv import ctmconv
from .slugs import generate_slug
from .. import models


class ScanException(Exception):
    pass


class AmbiguousZip(ScanException):
    pass


class NoAuthor(ScanException):
    pass


class InvalidAttachment(ScanException):
    pass


class Unpublishable(ScanException):
    pass


class ScanStore:
    def __init__(self, db):
        self.db = db
        pass

    def zip_upload(self, file, owner_id):
        """ Save the uploaded file as a zip file """
        # Allow uploading zip file.
        if file.filename.endswith('.zip'):
            # app.logger.warn('zip file, validate contents')
            print(file.stream)
            zip_file = ZipFile(file.stream, 'r', ZIP_DEFLATED)
            if (len(zip_file.infolist()) != 1):
                # app.logger.error('wrong number of files in zip')
                raise AmbiguousZip('ZIP uploads must contain exactly one file')
            # app.logger.warn('valid zip')
            return models.File.from_upload(file, models.File.MODELS_DIR, owner_id=owner_id)

        # Zip source file & save to large file storage
        # app.logger.warn('create empty zip')
        zip = models.File.from_name(file.filename + '.zip', models.File.MODELS_DIR, owner_id=owner_id)
        zip.mime_type = 'application/zip'

        filename, file_ext = os.path.splitext(file.filename)
        with tempfile.NamedTemporaryFile(suffix=file_ext) as uploadFile:
            # app.logger.warn('save upload to temp')
            file.save(uploadFile.name)
            with ZipFile(zip.get_absolute_path(), 'w', ZIP_DEFLATED) as zip_file:
                # app.logger.warn('write temp file to zip')
                zip_file.write(uploadFile.name, file.filename)

        # app.logger.warn('set zip size')
        zip.size = os.stat(zip.get_absolute_path()).st_size

        # app.logger.warn('generated zip')

        return zip

    def create(self, file, author_uri, data, attachments=[]):
        scan = self.new(author_uri)

        return self.update(scan, file, data, attachments)

    def new(self, author_uri):
        # Create instance of scan
        author = models.User.query.filter_by(email=author_uri).first()
        if author is None:
            raise NoAuthor('No author for ' + author_uri)

        scan = models.Scan(
            author_id=author.id
        )

        self.db.session.add(scan)

        return scan

    def update(self, scan, file, data, attachments=[]):
        author_id = scan.author_id
        # Save upload to temporary file
        if file:
            zip_file = self.zip_upload(file, author_id)
            scan.source = zip_file
            self.db.session.add(zip_file)

        scan.scientific_name = data.get('scientific_name')

        if (not scan.url_slug) and scan.scientific_name:
            scan.url_slug = generate_slug(scan.scientific_name)

        scan.alt_name = data.get('alt_name')
        scan.specimen_location = data.get('specimen_location')
        scan.specimen_id = data.get('specimen_id')
        scan.specimen_url = data.get('specimen_url')
        scan.description = data.get('description')
        scan.publications = data.get('publications')

        scan.tags = (data.get('geologic_age')
                     + data.get('ontogenic_age')
                     + data.get('elements'))

        gbif_id = data.get('gbif_id')

        if gbif_id and gbif_id != scan.gbif_id:
            from app.gbif import pull_tags

            scan.gbif_id = gbif_id
            tags = pull_tags(gbif_id)

            tag_ids = [tag.id for tag in tags]
            existing_tags = models.Taxonomy.query.filter(models.Taxonomy.id.in_(tag_ids)).all()
            existing_tag_ids = [tag.id for tag in existing_tags]
            scan.taxonomy = existing_tags

            for tag in tags:
                if tag.id in existing_tag_ids:
                    continue

                self.db.session.add(tag)
                scan.taxonomy.append(tag)

        for file in attachments:
            # if isinstance(file, Attachment):
            # 	continue

            # Take the filename as the label and generate a new, safe filename
            label = file.filename
            filename = secure_filename(file.filename) + '.png'

            file_model = models.File.from_binary(filename, file.stream, owner_id=author_id)

            if (file_model.mime_type != 'image/png'):
                raise InvalidAttachment('Stills must be png files')
            else:
                file.save(file_model.get_absolute_path())
                attachment = models.Attachment(
                    name=label,
                    file=file_model
                )
                self.db.session.add(attachment)
                scan.attachments.append(attachment)
        self.db.session.commit()
        return scan.url_slug

    def publish(self, scan_uri):
        scan = self.get(scan_uri)

        errors = []

        if not scan.source:
            errors.append('A scan file is required')

        if not scan.attachments:
            errors.append('A still is required')

        if (errors):
            raise Unpublishable('; '.join(errors))

        scan.published = True
        self.db.session.commit()

    def get(self, scan_uri):
        return models.Scan.find_by_slug(scan_uri)

    def create_ctm(self, scan):
        """ Convert an uploaded model file to a ctm file """
        if not isinstance(scan, models.Scan):
            scan = self.get(scan)

        if not scan.source:
            raise ScanException('Nothing to process; no file has been uploaded')

        zip = scan.source

        with ZipFile(zip.get_absolute_path(), 'r', ZIP_DEFLATED) as zipFile:
            upload_file_name = zipFile.infolist()[0].filename

            upload_file_data = zipFile.read(upload_file_name)

            filename, file_ext = os.path.splitext(upload_file_name)

            with tempfile.NamedTemporaryFile(suffix=file_ext) as uploadFile:
                uploadFile.write(upload_file_data)

                # Convert to bin if ascii
                uploadFile.seek(0)
                if uploadFile.read(5) == b'solid':
                    Mesh.from_file(uploadFile.name).save(uploadFile.name)

                # Convert to ctm in uploads storage
                ctm_file = models.File.from_name(filename + '.ctm', owner_id=scan.author_id)
                ctm_file.mime_type = 'application/octet-stream'

                ctmconv(uploadFile.name, ctm_file.get_absolute_path())

                ctm_file.size = os.stat(ctm_file.get_absolute_path()).st_size

                scan.ctm = ctm_file
                self.db.session.add(ctm_file)
                self.db.session.commit()

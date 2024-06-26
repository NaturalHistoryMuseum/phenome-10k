import os
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

import trimesh
from openctm import CTM, export_mesh
from stl.mesh import Mesh
from werkzeug.utils import secure_filename


class ScanStore:
    def __init__(self, db=None):
        self.db = db

    def init_app(self, db):
        self.db = db

    def zip_upload(self, file, owner_id):
        """
        Save the uploaded file as a zip file.
        """
        from ..models import File

        # Allow uploading zip file.
        if file.filename.endswith('.zip'):
            # app.logger.warn('zip file, validate contents')
            print(file.stream)
            zf = ZipFile(file.stream, 'r', ZIP_DEFLATED)
            if len(zf.infolist()) != 1:
                # app.logger.error('wrong number of files in zip')
                raise AmbiguousZip('ZIP uploads must contain exactly one file')
            # app.logger.warn('valid zip')
            return File.from_upload(file, File.MODELS_DIR, owner_id=owner_id)

        # Zip source file & save to large file storage
        # app.logger.warn('create empty zip')
        zip_file = File.from_name(
            file.filename + '.zip', File.MODELS_DIR, owner_id=owner_id
        )
        zip_file.mime_type = 'application/zip'

        filename, file_ext = os.path.splitext(file.filename)
        with tempfile.NamedTemporaryFile(suffix=file_ext) as upload_file:
            # app.logger.warn('save upload to temp')
            file.save(upload_file.name)
            with ZipFile(zip_file.get_absolute_path(), 'w', ZIP_DEFLATED) as zf:
                # app.logger.warn('write temp file to zip')
                zf.write(upload_file.name, file.filename)

        # app.logger.warn('set zip size')
        zip_file.size = os.stat(zip_file.get_absolute_path()).st_size

        # app.logger.warn('generated zip')

        return zip_file

    def create(self, file, author_uri, data, attachments=None):
        attachments = attachments or []
        scan = self.new(author_uri)

        return self.update(scan, file, data, attachments)

    def new(self, author_uri):
        # Create instance of scan
        from ..models import User, Scan

        author = User.query.filter_by(email=author_uri).first()
        if author is None:
            raise NoAuthor('No author for ' + author_uri)

        scan = Scan(author_id=author.id)

        self.db.session.add(scan)

        return scan

    def update(self, scan, file, data, attachments=None):
        from .slugs import generate_slug
        from ..models import Taxonomy, Attachment, File
        from .gbif import pull_tags, validate_id

        attachments = attachments or []
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
        scan.published = data.get('published')

        scan.tags = (
            data.get('geologic_age') + data.get('ontogenic_age') + data.get('elements')
        )

        gbif_occurrence_id = data.get('gbif_occurrence_id')
        if validate_id('occurrence', gbif_occurrence_id):
            scan.gbif_occurrence_id = gbif_occurrence_id

        gbif_species_id = data.get('gbif_species_id')
        if gbif_species_id != scan.gbif_species_id and validate_id(
            'species', gbif_species_id
        ):
            scan.gbif_species_id = gbif_species_id
            tags = pull_tags(gbif_species_id)
            tag_ids = [tag.id for tag in tags]
            existing_tags = Taxonomy.query.filter(Taxonomy.id.in_(tag_ids)).all()
            existing_tag_ids = [tag.id for tag in existing_tags]
            scan.taxonomy = existing_tags

            for tag in tags:
                if tag.id in existing_tag_ids:
                    continue

                self.db.session.add(tag)
                scan.taxonomy.append(tag)

        for file in attachments:
            # Take the filename as the label and generate a new, safe filename
            label = file.filename
            filename = secure_filename(file.filename) + '.png'

            file_model = File.from_binary(filename, file.stream, owner_id=author_id)

            if file_model.mime_type != 'image/png':
                raise InvalidAttachment('Stills must be png files')
            else:
                file.save(file_model.get_absolute_path())
                attachment = Attachment(name=label, file=file_model)
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

        if errors:
            raise Unpublishable('; '.join(errors))

        scan.published = True
        self.db.session.commit()

    def get(self, scan_uri):
        from ..models import Scan

        return Scan.find_by_slug(scan_uri)

    def create_ctm(self, scan):
        """
        Convert an uploaded model file to a ctm file.
        """
        from ..models import Scan, File

        if not isinstance(scan, Scan):
            scan = self.get(scan)

        if not scan.source:
            raise ScanException('Nothing to process; no file has been uploaded')

        zip_file = scan.source

        with ZipFile(zip_file.get_absolute_path(), 'r', ZIP_DEFLATED) as zf:
            upload_file_name = zf.infolist()[0].filename

            upload_file_data = zf.read(upload_file_name)

            filename, file_ext = os.path.splitext(upload_file_name)

            with tempfile.NamedTemporaryFile(suffix=file_ext) as upload_file:
                upload_file.write(upload_file_data)

                # Convert to bin if ascii
                upload_file.seek(0)
                if upload_file.read(5) == b'solid':
                    Mesh.from_file(upload_file.name).save(upload_file.name)

                # Convert to ctm in uploads storage
                ctm_file = File.from_name(filename + '.ctm', owner_id=scan.author_id)
                ctm_file.mime_type = 'application/octet-stream'

                self.ctmconv(upload_file.name, ctm_file.get_absolute_path())

                ctm_file.size = os.stat(ctm_file.get_absolute_path()).st_size

                scan.ctm = ctm_file
                self.db.session.add(ctm_file)
                self.db.session.commit()

    @classmethod
    def ctmconv(cls, source, dest):
        mesh = trimesh.load(source)
        ctm = CTM(mesh.vertices, mesh.faces, mesh.face_normals)
        export_mesh(ctm, dest)


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

import os

import pytest
from werkzeug.datastructures import FileStorage

from ..scan_store import ScanStore, AmbiguousZip, NoAuthor, InvalidAttachment, Unpublishable
from ... import app, db, models


class ObjectView(object):
    def __init__(self, d):
        self.__dict__ = d


@pytest.fixture
def database():
    """Create a client to test requests to the app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.testing = True

    # Set up the app context
    with app.app_context():
        # Create database and admin user
        db.create_all()

        user = models.User(
            name='Admin',
            email='admin',
            role='ADMIN'
        )
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()

        yield db

    # Empty database for next test
    db.drop_all()


@pytest.fixture
def store(database):
    return ScanStore(database)


@pytest.fixture
def zip_file():
    f = open(os.path.dirname(__file__) + '/test.zip', 'rb')

    yield f

    f.close()


@pytest.fixture
def empty_zip():
    f = open(os.path.dirname(__file__) + '/empty.zip', 'rb')

    yield f

    f.close()


@pytest.fixture
def image():
    f = open(os.path.dirname(__file__) + '/example.png', 'rb')

    yield f

    f.close()


@pytest.fixture
def horse():
    horse = open(os.path.dirname(__file__) + '/../../../fixtures/Horse.zip', 'rb')
    yield FileStorage(stream=horse, filename='horse.zip')
    horse.close()


def test_scan_store_create(store, image):
    file = ObjectView(dict(
        filename='my-file',
        stream='stream',
        save=lambda f: None
    ))
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None,
    }

    attachments = [
        FileStorage(
            stream=image,
            filename='image.png'
        )
    ]

    uri = store.create(
        file,
        'admin',
        data,
        attachments
    )

    scan = store.get(uri)

    for key, value in data.items():
        assert getattr(scan, key) == value


def test_scan_store_create_again(store):
    file = ObjectView(dict(
        filename='my-file',
        stream='stream',
        save=lambda f: None
    ))
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': 3,
        'attachments': []
    }

    uri1 = store.create(
        file,
        'admin',
        data
    )

    uri2 = store.create(
        file,
        'admin',
        data
    )

    scan = store.get(uri2)

    assert scan.url_slug == 'paul-2'


def test_zip_upload(store, zip_file):
    file = FileStorage(
        stream=zip_file,
        filename='my-file.zip'
    )
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None,
        'attachments': []
    }

    scan = store.get(store.create(file, 'admin', data))

    assert scan.source is not None


def test_empty_zip_upload(store, empty_zip):
    print(os.path.dirname(__file__) + '/test.zip')
    file = FileStorage(
        stream=empty_zip,
        filename='my-file.zip'
    )
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None,
        'attachments': []
    }

    with pytest.raises(AmbiguousZip):
        store.create(file, 'admin', data)


def test_no_author(store):
    print(os.path.dirname(__file__) + '/test.zip')
    file = {}
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None,
        'attachments': []
    }

    with pytest.raises(NoAuthor):
        store.create(file, 'paul', data)


def test_invalid_attachment(store, empty_zip):
    file = ObjectView(dict(
        filename='my-file',
        stream='stream',
        save=lambda f: None
    ))
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None
    }

    attachments = [
        FileStorage(
            stream=empty_zip,
            filename='zip.zip'
        )
    ]

    with pytest.raises(InvalidAttachment):
        uri = store.create(
            file,
            'admin',
            data,
            attachments
        )


def test_publish(store, zip_file, image):
    file = FileStorage(
        stream=zip_file,
        filename='my-file.zip'
    )
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None
    }

    attachments = [
        FileStorage(
            stream=image,
            filename='image.png'
        )
    ]

    uri = store.create(file, 'admin', data, attachments)
    store.publish(uri)
    scan = store.get(uri)

    assert scan.published


def test_unpublishable(store):
    file = None
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None
    }

    uri = store.create(file, 'admin', data)

    with pytest.raises(Unpublishable):
        store.publish(uri)


def test_create_ctm(store, horse):
    """Test to make sure an uploaded file gets processed"""
    data = {
        'scientific_name': 'Paul',
        'alt_name': 'alt name',
        'specimen_location': 'specimen_location',
        'specimen_id': 'specimen_id',
        # 'specimen_url': 'specimen_url',
        'description': 'description',
        'publications': [],
        'geologic_age': [],
        'ontogenic_age': [],
        'elements': [],
        'gbif_id': None
    }

    slug = store.create(horse, 'admin', data, [])
    store.create_ctm(slug)

    scan = store.get(slug)

    assert scan.ctm is not None

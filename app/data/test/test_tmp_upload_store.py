import pytest

from ..tmp_upload_store import TmpUploadStore


@pytest.fixture
def store():
    return TmpUploadStore('/tmp/upload_')


def test_get_name(store):
    with pytest.raises(ValueError):
        store.get_filepath('test')

    uuid = '22383093-099b-4823-9cbb-02f925b6423d'
    assert store.get_filepath(uuid) == '/tmp/upload_' + uuid


def test_write_to_file(store):
    file_id = store.create()

    store.append(file_id, b'string a')
    store.append(file_id, b'string b')

    with open(store.get_filepath(file_id), 'r') as file:
        assert file.read() == 'string astring b'

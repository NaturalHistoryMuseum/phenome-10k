from ..tmp_upload_store import TmpUploadStore
import pytest

@pytest.fixture
def store():
	return TmpUploadStore('/tmp/upload_')

def test_get_name(store):
	with pytest.raises(ValueError):
		store.getFilepath('test')

	uuid = '22383093-099b-4823-9cbb-02f925b6423d'
	assert store.getFilepath(uuid) == '/tmp/upload_'+uuid

def test_write_to_file(store):
	id = store.create()

	store.append(id, b'string a')
	store.append(id, b'string b')

	with open(store.getFilepath(id), 'r') as file:
		assert file.read() == 'string astring b'

import uuid


class TmpUploadStore:
    def __init__(self, prefix=None):
        self.prefix = prefix

    def init_app(self, app):
        self.prefix = app.config['TMP_UPLOAD']

    def get_filepath(self, file_id):
        # Validate the ID is a uuid
        uuid.UUID(file_id, version=4)
        return self.prefix + file_id

    def create(self):
        file_id = str(uuid.uuid4())
        return file_id

    def append(self, file_id, data):
        filename = self.get_filepath(file_id)
        file = open(filename, 'ab')
        file.write(data)
        file.close()

import uuid


class TmpUploadStore:
    def __init__(self, prefix):
        self.prefix = prefix

    def get_filepath(self, id):
        # Validate the ID is a uuid
        uuid.UUID(id, version=4)
        return self.prefix + id

    def create(self):
        id = str(uuid.uuid4())
        return id

    def append(self, id, data):
        filename = self.get_filepath(id)
        file = open(filename, 'ab')
        file.write(data)
        file.close()

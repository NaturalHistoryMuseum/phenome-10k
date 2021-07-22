from ..server import TaskExecutor


class MockQueue:
    def __init__(self, items=[]):
        self.queue = items

    def read(self):
        for item in self.queue:
            yield item


class MockScanStore:
    def __init__(self):
        self.calls = []

    def create_ctm(self, slug):
        self.calls.append(slug)

        if slug == '3':
            raise Exception("I don't like the number three.")


def test_create_ctm():
    s = MockScanStore()
    q = MockQueue([
        ('create_ctm', ('1',)),
        ('invalid', ('2',)),
        ('create_ctm', ('3',)),
    ])

    server = TaskExecutor(q, s)
    server.run()

    assert s.calls == ['1', '3']

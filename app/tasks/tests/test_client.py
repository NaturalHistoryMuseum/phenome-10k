from ..client import TaskQueue


class MockQueue:
    def __init__(self):
        self.queue = []

    def add(self, task, *args):
        self.queue.append((task, args))


def test_create_ctm():
    q = MockQueue()
    client = TaskQueue(q)

    client.create_ctm('slug')

    assert q.queue == [('create_ctm', ('slug',))]

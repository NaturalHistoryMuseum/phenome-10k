class TaskQueue:
    def __init__(self, QueueModel):
        self.queue = QueueModel

    def create_ctm(self, scan_slug):
        self.queue.add('create_ctm', scan_slug)

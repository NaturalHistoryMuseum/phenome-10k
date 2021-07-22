class TaskQueue:
    def __init__(self, queue_model):
        self.queue = queue_model

    def create_ctm(self, scan_slug):
        self.queue.add('create_ctm', scan_slug)

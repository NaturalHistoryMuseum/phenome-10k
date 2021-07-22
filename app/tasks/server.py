class TaskExecutor:
    def __init__(self, queue_model, scan_store):
        self.queue = queue_model
        self.scan_store = scan_store
        self.methods = {
            'create_ctm': lambda slug: scan_store.create_ctm(slug)
        }

    def execute(self, task):
        (method, args) = task
        function = self.methods.get(method, None)

        print(method, args)
        if function is None:
            print('No function for method ' + method)
        else:
            function(*args)

    def next(self):
        task = self.queue.get()
        if task is None:
            return False

        self.execute(task)

        return True

    def run(self):
        for task in self.queue.read():
            try:
                self.execute(task)
            except Exception as err:
                print(err)

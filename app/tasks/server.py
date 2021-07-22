class TaskExecutor:
    def __init__(self, QueueModel, scanStore):
        self.queue = QueueModel
        self.scanStore = scanStore
        self.methods = {
            'create_ctm': lambda slug: scanStore.create_ctm(slug)
        }

    def execute(self, task):
        (method, args) = task
        function = self.methods.get(method, None)

        print(method, args)
        if function == None:
            print('No function for method ' + method)
        else:
            function(*args)

    def next(self):
        task = self.queue.get()
        if task == None:
            return False

        self.execute(task)

        return True

    def run(self):
        for task in self.queue.read():
            try:
                self.execute(task)
            except Exception as err:
                print(err)

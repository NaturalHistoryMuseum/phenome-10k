class TaskExecutor:
	def __init__(self, QueueModel, scanStore):
		self.queue = QueueModel
		self.scanStore = scanStore
		self.methods = {
			"create_ctm": lambda slug: scanStore.create_ctm(slug)
		}

	def run(self):
		for (method, args) in self.queue.read():
			try:
				function = self.methods.get(method, None)
				print(method, args)
				if function == None:
					print("No function for method " + method)
				else:
					function(*args)
			except Exception as err:
				print(err)

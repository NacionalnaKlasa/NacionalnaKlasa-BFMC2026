from threading import Lock

class Queue:
	def __init__(self):
		self.Queue = []
		self.size = 0
		self.lock = Lock()

	def pop(self):
		with self.lock:
			if self.size > 0:
				self.size = self.size - 1
				return self.Queue.pop(0)
		
		return None
	
	def append(self, elem):
		with self.lock:
			self.Queue.append(elem)
			self.size = self.size + 1

			return True

	def __len__(self):
		with self.lock:
			return self.size
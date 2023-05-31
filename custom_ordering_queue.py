class CustomOrderingQueue:
    def __init__(self, sorter=lambda x: x.key):
        self._queue = []
        self.sorter = sorter

    def append(self, item):
        self._queue.append(item)

    def popleft(self):
        self._queue.sort(key=self.sorter, reverse=True)
        return self._queue.pop()

    def __len__(self):
        return len(self._queue)

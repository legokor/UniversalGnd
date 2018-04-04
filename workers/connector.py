import threading


class Connector:
    def __init__(self):
        self._listening = False
        self._callback = lambda: None

    def start__listening(self, callback):
        self._callback = callback
        if not self.listening:
            thread = threading.Thread(target=self.listen)
            thread.daemon = True
            thread.start()
        self._listening = True

    def stop__listening(self):
        if self.listening:
            self.destruct()
        self._listening = False

    @property
    def listening(self):
        return self._listening

    @property
    def callback(self):
        return self._callback

    def send(self, message):
        pass

    def listen(self):
        pass

    def destruct(self):
        pass

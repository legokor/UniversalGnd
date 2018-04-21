import socket
import threading

from .connector import Connector


class SocketConnector(Connector):
    def __init__(self, ip, port):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        # self.socket.listen(5)

    def send(self, message):
        self.socket.send(bytes(message, 'UTF-8'))

    def digest_message(self, connection):
        while self.listening:
            self.callback(connection.recv(1))

    def thread_listen(self):
        while self.listening:
            connection, address = self.socket.accept()
            thread = threading.Thread(target=self.digest_message, args=(connection,))
            thread.daemon = True
            thread.start()

    def listen(self):
        thread = threading.Thread(target=self.thread_listen)
        thread.daemon = True
        # thread.start()

    def destruct(self):
        self.socket.close()

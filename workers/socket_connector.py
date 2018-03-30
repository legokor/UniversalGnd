import socket


class SocketConnector:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.listening = False

    def send(self, message):
        self.socket.send(bytes(message, 'UTF-8'))

    def start_listening(self, callback):
        self.listening = True

    def stop_listening(self):
        self.listening = False

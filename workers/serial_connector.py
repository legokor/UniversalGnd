import serial

from .connector import Connector


class SerialConnector(Connector):
    def __init__(self, baud, port):
        super().__init__()
        self.connection = serial.Serial()
        self.connection.baudrate = baud
        self.connection.port = port
        self.connection.open()

    def send(self, message):
        self.connection.write(message.encode('ascii'))

    def listen(self):
        while self.listening:
            message = self.connection.read(64)
            self.callback(message)

    def destruct(self):
        self.connection.close()


class UpraConnector(SerialConnector):
    message_format = '^\$\$(.{7}),(.{3}),(.{2})(.{2})(.{2}),([+-].{4}\..{3}),([+-].{5}\..{3}),(.{5}),(.{4}),(.{3}),(.{3}),$'

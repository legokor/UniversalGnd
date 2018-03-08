import threading
from channels import Group
import socket
import json
import struct
from datetime import datetime


listening = False
client_socket = None

time_start = 0


def connect_socket():
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 54321))
    return clientsocket


def send_message(socket, message):
    socket.send(bytes(message, 'UTF-8'))


def process_message(data):
    global time_start
    (messageId, timestamp, dataCount, data0, data1, data2, data3) = data
    if messageId == 1:
        send_coordinates({"latitude": data0, "longitude": data1})
    if messageId == 2:
        send_raw({"timestamp": timestamp, "altitude": data0})
    if messageId == 3:
        send_raw({"timestamp": timestamp, "speed": data0})


def digest_message(connection):
    global time_start

    string = b''
    while True:
        buf = connection.recv(1)
        if len(buf) > 0:
            string += buf
            if len(string) == 22:
                process_message(struct.unpack('<BIBffff', string))
                string = b''


def listener():
    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_socket.bind(('localhost', 12345))
    listener_socket.listen(5)
    print("starting listener")

    while True:
        connection, address = listener_socket.accept()
        print(connection, address)
        thread = threading.Thread(target=digest_message, args=(connection,))
        thread.start()


def send_raw(data):
    Group("listeners").send({
        "text": json.dumps(data),
    })


def send_coordinates(coordinates):
    global time_start
    Group("listeners").send({
        "text": json.dumps({"lat": coordinates['latitude'], "lng": coordinates['longitude']}),
    })
    time_start = datetime.now()


def ws_connect(message):
    global listening
    message.reply_channel.send({"accept": True})
    Group("listeners").add(message.reply_channel)
    if not listening:
        listening = True
        thread = threading.Thread(target=listener, args=())
        thread.daemon = True
        thread.start()


def ws_receive(message):
    global client_socket, time_start
    print(datetime.now() - time_start)
    # if client_socket is None:
    #     client_socket = connect_socket()
    # send_message(client_socket, message.content['text'])


def ws_disconnect(message):
    Group("listeners").discard(message.reply_channel)

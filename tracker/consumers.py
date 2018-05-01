import json
import re
from functools import partial

import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from workers.serial_connector import SerialConnector
from workers.socket_connector import SocketConnector
from workers.wrapper import Wrapper
from .models import Launch


def broadcast(message):
    layer = channels.layers.get_channel_layer()
    async_to_sync(layer.group_send)(
        "group",
        {
            'type': "basic_send",
            'message': message,
        }
    )


def broadcast_string(message):
    broadcast({'message': message})


def parse_upra(message):
    match = re.match(UPRA_STRING, message)
    broadcast({'type': 'upra', 'data': {
        'callsign': match.group(1),
        'messageid': match.group(2),
        'hours': match.group(3),
        'minutes': match.group(4),
        'seconds': match.group(5),
        'latitude': match.group(6),
        'longitude': match.group(7),
        'altitude': match.group(8),
        'externaltemp': match.group(9),
        'obctemp': match.group(10),
        'comtemp': match.group(11),
    }})


def mam_transfer(callback, message):
    try:
        message = MAM_MESSAGES[message]
    except KeyError:
        pass
    else:
        broadcast_string(message)
        callback(message)


UPRA_STRING = r'\$\$(.{7}),(.{3}),(.{2})(.{2})(.{2}),([+-].{4}\..{3}),([+-].{5}\..{3}),(.{5}),(.{4}),(.{3}),(.{3}),'

MAM_MESSAGES = {
    '11111110': 'ELORE',
    '11111101': 'HATRA',
    '11111011': 'JOBBRA',
    '11110111': 'BALRA',
    '11101111': 'KARLE',
    '11011111': 'KARFEL',
    '10111111': 'VILLOG',
    '01111111': 'MEGALL',
}


class Consumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrapper = None
        self.connector = None
        self.connector_socket = None
        self.wrapper_socket = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            "group",
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "group",
            self.channel_name
        )

    def basic_send(self, event):
        self.send(text_data=json.dumps(event['message']))

    def task_update(self, event):
        self.send(text_data=json.dumps({'taskData': event['message']}))

    def receive(self, text_data):
        data = json.loads(text_data)
        if data['action'] == 'init':
            if data['target'] == 'mam':
                self.connector = SerialConnector(115200, 'COM4')
                self.connector_socket = SocketConnector('192.168.4.1', 1360)
                self.wrapper_socket = Wrapper(r'.*', broadcast_string, self.connector_socket.send)
                bound = partial(mam_transfer, self.connector_socket.send)
                self.connector_socket.start_listening(callback=self.wrapper_socket.consume_character)
                self.wrapper = Wrapper(r'\d{8}', bound, self.connector.send)
                self.connector.start_listening(callback=self.wrapper.consume_character)

            if data['target'] == 'upra':
                self.connector = SocketConnector('127.0.0.1', 1337)
                self.wrapper = Wrapper(UPRA_STRING, parse_upra, self.connector.send)
                self.connector.start_listening(callback=self.wrapper.consume_character)

        if data['action'] == 'button-click':
            if self.wrapper:
                message = MAM_MESSAGES.get(str(data['id']), '')
                self.wrapper.send(message)

        if data['action'] == 'send':
            if self.wrapper:
                self.wrapper.send(data['data'])

        if data['action'] == 'fetch':
            try:
                launch = Launch.objects.get(pk=data['id'])
            except Launch.DoesNotExist:
                self.send(text_data=json.dumps({'message': 'Does not exist'}))
            else:
                self.send(text_data=json.dumps({'tasks': [task.serialized_fields() for task in launch.task_set.all()]}))

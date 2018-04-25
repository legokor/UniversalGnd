import json
import re

import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

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
    print('sending string: ' + message)
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


UPRA_STRING = r'\$\$(.{7}),(.{3}),(.{2})(.{2})(.{2}),([+-].{4}\..{3}),([+-].{5}\..{3}),(.{5}),(.{4}),(.{3}),(.{3}),'

MAM_MESSAGES = {
    '1': 'ELORE',
    '2': 'HATRA',
    '3': 'JOBBRA',
    '4': 'BALRA',
    '5': 'KARLE',
    '6': 'KARFEL',
    '7': 'VILLOG',
    '8': 'MEGALL',
}


def initiate_upra_wrapper(address, port):
    sc = SocketConnector(address, port)
    wrapper = Wrapper(UPRA_STRING, broadcast, sc.send)
    sc.callback = wrapper.consume_character


class Consumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrapper = None
        self.connector = None

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
                self.connector = SocketConnector('127.0.0.1', 1360)
                self.wrapper = Wrapper(r'.*', broadcast_string, self.connector.send)
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

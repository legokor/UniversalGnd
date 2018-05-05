import json
import re
import struct
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


def parse_mam(message):
    if message[0:4] == 'ADCN':
        print(struct.unpack('!ccccIfI', bytes(message, 'utf-8')))
    if message[0:4] == 'VOLT':
        print(struct.unpack('!ccccfII', bytes(message, 'utf-8')))


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


MAM_STATE = 'VEHICLE'
MAM_MOVING_FORWARD = False
MAM_MOVING_BACKWARD = False
MAM_PIN_DOWN = False
MAM_POT_STATE = 50


def parse_mam(callback, message):
    global MAM_STATE, MAM_MOVING_BACKWARD, MAM_MOVING_FORWARD, MAM_POT_STATE

    match = re.match(MAM_STRING, message)
    data = {
        'switch-1': int(match.group(1)[0]),
        'switch-2': int(match.group(1)[1]),
        'switch-3': int(match.group(1)[2]),
        'switch-4': int(match.group(1)[3]),
        'button-1': int(match.group(2)[0]),
        'button-2': int(match.group(2)[1]),
        'pot': int(match.group(3)),
        'mode': MAM_STATE,
        'moving-forward': MAM_MOVING_FORWARD,
        'moving-backward': MAM_MOVING_BACKWARD,
    }
    broadcast({'type': 'mam', 'data': data})
    if MAM_STATE == 'VEHICLE':
        print('vehicle state')
        if data['switch-1'] == 0:
            callback('FOWD')
            MAM_MOVING_FORWARD = True
        elif MAM_MOVING_FORWARD:
            MAM_MOVING_FORWARD = False
            callback('STOP')
        if data['switch-2'] == 0:
            callback('BAWD')
            MAM_MOVING_BACKWARD = True
        elif MAM_MOVING_BACKWARD:
            MAM_MOVING_BACKWARD = False
            callback('STOP')
        if data['switch-3'] == 0:
            callback('LEFT')
        if data['switch-4'] == 0:
            callback('RGHT')
        if data['button-1'] == 0:
            callback('STOP')
            MAM_MOVING_FORWARD = False
            MAM_MOVING_BACKWARD = False
        if data['button-2'] == 0:
            MAM_STATE = 'PIN'
        if data['pot'] != MAM_POT_STATE:
            if data['pot'] < MAM_POT_STATE:
                callback('LEFT')
            else:
                callback('RGHT')
            MAM_POT_STATE = data['pot']
    else:
        print('pin state')
        if data['switch-1'] == 0:
            callback('PNUP')
        if data['switch-2'] == 0:
            callback('PNDN')
        if data['switch-3'] == 0:
            callback('PNLT')
        if data['switch-4'] == 0:
            callback('PNGT')
        if data['button-1'] == 0:
            callback('STOP')
        if data['button-2'] == 0:
            MAM_STATE = 'VEHICLE'

    data.update({
        'mode': MAM_STATE,
        'moving-forward': MAM_MOVING_FORWARD,
        'moving-backward': MAM_MOVING_BACKWARD
    })
    broadcast({'type': 'mam', 'data': data})


UPRA_STRING = r'\$\$(.{7}),(.{3}),(.{2})(.{2})(.{2}),([+-].{4}\..{3}),([+-].{5}\..{3}),(.{5}),(.{4}),(.{3}),(.{3}),'
MAM_STRING = r'(\d{4})(\d{2})(\d{3})'


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
        print(data)

        if data['action'] == 'init':
            if data['target'] == 'mam':
                self.connector = SerialConnector(115200, data['com'])
                self.connector_socket = SocketConnector('192.168.4.1', 1360)
                self.wrapper_socket = Wrapper(r'.*', broadcast_string, self.connector_socket.send)
                bound = partial(parse_mam, self.connector_socket.send)
                self.connector_socket.start_listening(callback=self.wrapper_socket.consume_character)
                self.wrapper = Wrapper(MAM_STRING, bound, self.connector.send)
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

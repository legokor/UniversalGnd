import json
import re
from functools import partial

import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from workers.console_connector import ConsoleConnector
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
    global MAM_RECEIVED, MAM_SENT
    MAM_RECEIVED = True
    MAM_SENT = False
    broadcast({'message': message})


def parse_upra(message):
    match = re.search(UPRA_STRING, message)
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
MAM_SENT = False
MAM_RECEIVED = False


def parse_mam(callback, message):
    global MAM_STATE, MAM_MOVING_BACKWARD, MAM_MOVING_FORWARD, MAM_POT_STATE, MAM_PIN_DOWN, MAM_SENT, MAM_RECEIVED

    if MAM_SENT and not MAM_RECEIVED:
        print('Missing an ACK...')

    match = re.search(MAM_STRING, message)
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
    if data['switch-1'] == 0:
        pass
    if data['switch-2'] == 0:
        callback('STOP')
        MAM_MOVING_BACKWARD = False
        MAM_MOVING_FORWARD = False
    if data['switch-3'] == 0:
        callback('PNDN')
        MAM_PIN_DOWN = True
    elif MAM_PIN_DOWN:
        callback('PNUP')
        MAM_PIN_DOWN = False
    if data['switch-4'] == 0:
        MAM_STATE = 'PIN'
    elif MAM_STATE == 'PIN':
        MAM_STATE = 'VEHICLE'
    if data['button-1'] == 0:
        callback('FOWD')
        MAM_MOVING_FORWARD = True
    elif MAM_MOVING_FORWARD:
        MAM_MOVING_FORWARD = False
        callback('STOP')
    if data['button-2'] == 0:
        callback('BAWD')
        MAM_MOVING_BACKWARD = True
    elif MAM_MOVING_BACKWARD:
        MAM_MOVING_BACKWARD = False
        callback('STOP')
    if data['pot'] != MAM_POT_STATE:
        if MAM_STATE == 'VEHICLE':
            callback('X' + str(data['pot']).zfill(3))
        else:
            callback('Q' + str(data['pot']).zfill(3))
        MAM_POT_STATE = data['pot']

    data.update({
        'mode': MAM_STATE,
        'moving-forward': MAM_MOVING_FORWARD,
        'moving-backward': MAM_MOVING_BACKWARD
    })
    MAM_SENT = True
    MAM_RECEIVED = False
    broadcast({'type': 'mam', 'data': data})


UPRA_STRING = r'\$\$(.{7}),(.{3}),(.{2})(.{2})(.{2}),([+-]?.{4}\..{3}),([+-]?.{5}\..{3}),(.{5}),(.{4}),(.{3}),(.{3}),'
MAM_STRING = r'(\d{4})(\d{2})(\d{3})'


class Consumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrapper = None
        self.connector = None
        self.connector_socket = None
        self.wrapper_socket = None
        self.process = None
        self.process_predictor = None
        self.selected_launch = None

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

    def handle_upra_packet(self, packet_str):
        parse_upra(packet_str)
        if self.process_predictor is not None:
            self.process_predictor.send({
                'cmd': 'senduprapacket',
                'flightname': self.selected_launch.name,
                'packet': packet_str})
            self.process_predictor.send({
                'cmd': 'predict',
                'flightname': self.selected_launch.name,
                'timestep': 5})

    def handle_predictor_output(self, output_str):
        output = json.loads(output_str)
        if 'prediction' in output:
            self.send(text_data=json.dumps(
                {'type': 'upra', 'prediction': output['prediction']}))
        if 'bprops' in output:
            self.send(text_data=json.dumps(
                {'type': 'upra', 'bprops': output['bprops']}))
        if 'msg' in output:
            self.send(text_data=json.dumps(
                {'message': '[Predictor] ' + output['msg']}))

    def setup_mam_2018(self, data):
        self.connector = SerialConnector(115200, data['com'])
        self.connector_socket = SocketConnector('192.168.4.1', 1360)
        self.wrapper_socket = Wrapper(r'.*', broadcast_string, self.connector_socket.send)
        bound = partial(parse_mam, self.connector_socket.send)
        self.connector_socket.start_listening(callback=self.wrapper_socket.consume_character)
        self.wrapper = Wrapper(MAM_STRING, bound, self.connector.send)
        self.connector.start_listening(callback=self.wrapper.consume_character)

    def setup_upra(self, data):
        self.connector = SerialConnector(57600, data['com'])
        self.wrapper = Wrapper(UPRA_STRING, handle_upra_packet, self.connector.send)
        self.connector.start_listening(callback=self.wrapper.consume_character)

    def setup_predictor(self):
        self.process_predictor = ConsoleConnector('predictor')
        # TODO: Handle executable not found
        self.process_predictor.start_listening(callback=self.handle_predictor_output)

    def receive(self, text_data):
        data = json.loads(text_data)

        if data['action'] == 'init':
            if data['target'] == 'mam':
                self.setup_mam_2018(data)

            if data['target'] == 'upra':
                self.setup_upra(data)

            if data['target'] == 'predictor':
                self.setup_predictor()

        if data['action'] == 'send':
            self.connector_socket.send(data['data'])

        if data['action'] == 'get-launches':
            self.send(text_data=json.dumps({'launches': [
                {'id': launch.id, 'name': launch.name} for launch in Launch.objects.all()
            ]}))

        if data['action'] == 'fetch-launch':
            try:
                launch = Launch.objects.get(pk=data['id'])
            except Launch.DoesNotExist:
                self.send(text_data=json.dumps({'message': 'Does not exist'}))
            else:
                self.selected_launch = launch
                self.send(text_data=json.dumps({'type': 'checklist', 'tasks': launch.get_organized_tasks()}))

        if data['action'] == 'program-name':
            self.process = ConsoleConnector(data['data'])
            self.process.start_listening(callback=broadcast_string)

        if data['action'] == 'program-command':
            if self.process is not None:
                self.process.send(data['data'])

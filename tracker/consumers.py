import json
import re
from functools import partial
from datetime import datetime

import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import SyncConsumer

from workers.console_connector import ConsoleConnector
from workers.serial_connector import SerialConnector
from workers.socket_connector import SocketConnector
from workers.wrapper import Wrapper
from .models import Launch
from .weatherdata import getWeatherData


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


MAM_STRING = r'(\d{4})(\d{2})(\d{3})'


class Consumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrapper = None
        self.connector = None
        self.connector_socket = None
        self.wrapper_socket = None
        self.process = None
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
        if self.selected_launch is not None:
            async_to_sync(self.channel_layer.group_discard)(
                self.selected_launch.name,
                self.channel_name
            )

    def basic_send(self, event):
        self.send(text_data=json.dumps(event['message']))

    def task_update(self, event):
        self.send(text_data=json.dumps({'taskData': event['message']}))

    def select_launch(self, launch):
        self.selected_launch = launch
        async_to_sync(self.channel_layer.group_add)(
            self.selected_launch.name,
            self.channel_name
        )

    def setup_mam_2018(self, data):
        self.connector = SerialConnector(115200, data['com'])
        self.connector_socket = SocketConnector('192.168.4.1', 1360)
        self.wrapper_socket = Wrapper(r'.*', broadcast_string, self.connector_socket.send)
        bound = partial(parse_mam, self.connector_socket.send)
        self.connector_socket.start_listening(callback=self.wrapper_socket.consume_character)
        self.wrapper = Wrapper(MAM_STRING, bound, self.connector.send)
        self.connector.start_listening(callback=self.wrapper.consume_character)

    def setup_upra(self, data):
        if self.selected_launch is None:
            self.send(text_data=json.dumps({
                'message': 'You need to select a launch before connecting.'}))
            return

        async_to_sync(self.channel_layer.send)('upra-gnd',
            {'type': 'upra.connect', 'port': data['com'], 'baud': 57600, 'mission': self.selected_launch.name})

    def setup_predictor(self, data):
        if self.selected_launch == None:
            self.send(text_data=json.dumps({
                'message': 'Cannot initialize predictor: No launch selected.'}))
            return

        balloonprops = self.selected_launch.get_balloon_properties()
        for propname in balloonprops:
            if balloonprops[propname] is None:
                self.send(text_data=json.dumps({
                    'message': 'Cannot initialize predictor: Balloon property '+propname+' has no value.'}))
                return

        weatherdate = datetime.strptime(data['weatherdate'], "%Y-%m-%d %H:%M")

        async_to_sync(self.channel_layer.send)('upra-gnd', {
            'type': 'upra.predictor.start',
        })
        async_to_sync(self.channel_layer.send)('upra-gnd', {
            'type': 'upra.predictor.newflight',
            'mission': self.selected_launch.name,
            'bprops': self.selected_launch.get_balloon_properties(),
            'weatherdate': weatherdate
        })

    def rawpacket(self, event):
        self.send(text_data=json.dumps(event))

    def location_upra(self, event):
        self.send(text_data=json.dumps(event))

    def temperature_upra(self, event):
        self.send(text_data=json.dumps(event))

    def upra_tlmpacket(self, event):
        self.send(text_data=json.dumps({
            'type': 'upra',
            'data': event['data']
        }))

    def upra_balloonprops_set(self, event):
        if self.selected_launch is None:
            self.send(text_data=json.dumps({
                'message': 'You need to select a launch before setting balloon props'}))
            return

        for propname in self.selected_launch.get_balloon_properties():
            if propname in event:
                setattr(self.selected_launch, propname, float(event[propname]));
                self.selected_launch.save()

    def upra_gnd_frequency_set(self, event):
        if self.selected_launch is None:
            self.send(text_data=json.dumps({
                'message': 'You need to select a launch before setting radio frequency'}))
            return

        event['mission'] = self.selected_launch.name
        async_to_sync(self.channel_layer.send)('upra-gnd', event)

    def upra_predictor_balloonprops(self, event):
        packet = event['balloonprops']
        packet['type'] = 'upra.balloonprops'

        self.send(text_data=json.dumps(packet))

    def upra_predictor_prediction(self, event):
        self.send(text_data=json.dumps({
            'type': 'upra',
            'prediction': event['prediction']
        }))

    def receive(self, text_data):
        data = json.loads(text_data)

        if 'action' not in data:
            # Send this to ourselves as a channels event
            async_to_sync(self.channel_layer.send)(self.channel_name, data);
            return

        if data['action'] == 'init':
            if data['target'] == 'mam':
                self.setup_mam_2018(data)

            if data['target'] == 'upra':
                self.setup_upra(data)

            if data['target'] == 'predictor':
                self.setup_predictor(data)

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
                self.select_launch(launch)
                self.send(text_data=json.dumps({'type': 'checklist', 'tasks': launch.get_organized_tasks()}))
                balloonprops = launch.get_balloon_properties()
                balloonprops['type'] = 'upra.balloonprops'
                self.send(text_data=json.dumps(balloonprops))


        if data['action'] == 'program-name':
            self.process = ConsoleConnector(data['data'])
            self.process.start_listening(callback=broadcast_string)

        if data['action'] == 'program-command':
            if self.process is not None:
                self.process.send(data['data'])


class UpraGndWorker(SyncConsumer):

    UPRA_STRING = r'\$\$(.{7}),(.{3}),(.{2})(.{2})(.{2}),([+-]?.{4}\..{3}),([+-]?.{5}\..{3}),(.{5}),(.{4}),(.{3}),(.{3}),'

    def __init__(self, *args, **kwargs):
        self.connections = {}

        self.flights_with_prediction = []
        self.process_predictor = None

    def parse_upra(self, launchname, message):
        match = re.search(self.UPRA_STRING, message)
        async_to_sync(self.channel_layer.group_send)(launchname, {
            'type': 'upra.tlmpacket',
            'data': {
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
            }
        })

    def handle_upra_packet(self, launchname, packet_str):
        self.parse_upra(launchname, packet_str)
        if self.process_predictor is not None:
            self.process_predictor.send(json.dumps({
                'cmd': 'senduprapacket',
                'flightname': launchname,
                'packet': packet_str}))
            self.process_predictor.send(json.dumps({
                'cmd': 'predict',
                'flightname': launchname,
                'timestep': 5}))

    def handle_predictor_output(self, output_str):
        output = json.loads(output_str)
        if 'prediction' in output:
            async_to_sync(self.channel_layer.group_send)(output['flightname'], {
                'type': 'upra.predictor.prediction',
                'prediction': output['prediction']
            })
        if 'bprops' in output:
            async_to_sync(self.channel_layer.group_send)(output['flightname'], {
                'type': 'upra.predictor.balloonprops',
                'balloonprops': output['bprops']
            })


    def upra_connect(self, event):
        if event['mission'] in self.connections:
            return

        connector = None
        if event['port'] == 'simulator':
            connector = SocketConnector('0.0.0.0', 1337)
        else:
            connector = SerialConnector(event['baud'], event['port'])

        self.connections[event['mission']] = Wrapper(
            self.UPRA_STRING,
            partial(self.handle_upra_packet, event['mission']),
            connector.send)
        connector.start_listening(
            callback=self.connections[event['mission']].consume_character)

    def upra_gnd_frequency_set(self, event):
        if event['mission'] not in self.connections:
            return
        freq = int(float(event['freq'])*1000)
        self.connections[event['mission']].send( '$GRSFQ,'+str(freq)+',*cc' )

    def upra_predictor_start(self, event):
        if self.process_predictor is not None:
            return

        self.process_predictor = ConsoleConnector('./predictor')
        # TODO: Handle executable not found
        self.process_predictor.start_listening(callback=self.handle_predictor_output)

    def upra_predictor_newflight(self, event):
        if event['mission'] in self.flights_with_prediction:
            return

        bprops = event['bprops']

        self.process_predictor.send(json.dumps({
            'cmd': 'newflight',
            'flightname': event['mission'],
            'balloonprops': {
                'balloon_dry_mass': bprops['balloon_dry_mass']/1000,
                'parachute_dry_mass': bprops['parachute_dry_mass']/1000,
                'payload_dry_mass': bprops['payload_dry_mass']/1000,
                'nozzle_lift': bprops['nozzle_lift']/1000,
                'parachute_area': bprops['parachute_area'],
                'parachute_drag_c': bprops['parachute_drag_c'],
                'balloon_drag_c': bprops['balloon_drag_c'],
                'design_burst_diam': bprops['design_burst_diam']
            },
            'weatherdata': getWeatherData(event['weatherdate'])
        }))

        self.flights_with_prediction.append(event['mission'])

    

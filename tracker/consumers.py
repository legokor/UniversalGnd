import channels.layers
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

from .models import Launch
from workers.socket_connector import SocketConnector
from workers.wrapper import Wrapper


def broadcast(message):
    layer = channels.layers.get_channel_layer()
    async_to_sync(layer.group_send)(
        "group",
        {
            'type': "task_update",
            'message': message,
        }
    )


UPRA_STRING = r'^\$\$(.{7}),(.{3}),(.{2})(.{2})(.{2}),([+-].{4}\..{3}),([+-].{5}\..{3}),(.{5}),(.{4}),(.{3}),(.{3}),$'

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

    def task_update(self, event):
        self.send(text_data=json.dumps({'taskData': event['message']}))

    def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        if data['action'] == 'init':
            if data['target'] == 'mam':
                self.connector = SocketConnector('127.0.0.1', 1360)
                self.wrapper = Wrapper(r'.', broadcast, self.connector.send)
                self.connector.callback = self.wrapper.consume_character
                self.connector.listen()

        if data['action'] == 'button-click':
            if self.wrapper:
                message = MAM_MESSAGES.get(str(data['id']), '')
                print('msg:' + message)
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

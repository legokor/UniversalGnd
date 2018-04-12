import channels.layers
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

from .models import Launch


def broadcast(message):
    layer = channels.layers.get_channel_layer()
    async_to_sync(layer.group_send)(
        "group",
        {
            'type': "task_update",
            'message': message,
        }
    )


class Consumer(WebsocketConsumer):
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
        if data['action'] == 'fetch':
            try:
                launch = Launch.objects.get(pk=data['id'])
            except Launch.DoesNotExist:
                self.send(text_data=json.dumps({'message': 'Does not exist'}))
            else:
                self.send(text_data=json.dumps({'tasks': [task.serialized_fields() for task in launch.task_set.all()]}))

import channels.layers
from asgiref.sync import async_to_sync

from channels.generic.websocket import JsonWebsocketConsumer
from .models import Launch


class RadioStationConsumer(JsonWebsocketConsumer):
    """Handles an UGND ARS connection"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The mission (Launch) this ARS is currently operating for
        self.mission = None
        # Name of this station
        self.name = None

        # Position of the station
        self.latitude = None
        self.longitude = None
        self.altitude = None

        # Message types that just need to be forwarded to clients
        self.forwarded_types = ['rawpacket']

    def layer_group_name_decorate(self, group_name):
        return group_name+'-ars'

    def attributes_missing(self, event, required_attrs, send_error=True):
        for attr in required_attrs:
            if attr not in event:
                if send_error:
                    self.send_json({'type':'error', 'message':'Missing '+attr+' attribute'})
                return True
        return False

    def send_to_clients(self, event, throw=False):
        """
        Send the packet to all clients watching this mission
        (consumers in the group of the mission's name).
        """

        if self.mission is None:
            if throw:
                raise RuntimeError
            else:
                self.send_json({'type':'error', 'message':'You need to select a mission before sending data'})
        else:
            async_to_sync(self.channel_layer.group_send)(self.mission.name, event)


    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        if self.mission is not None:
            async_to_sync(self.channel_layer.group_discard)(
                self.layer_group_name_decorate(self.mission.name),
                self.channel_name
            )

    def receive_json(self, content=None):
        if content is None or self.attributes_missing(content, ['type']):
            return

        # See if we only need to forward this
        if content['type'] in self.forwarded_types:
            try:
                self.send_to_clients(content)
            except RuntimeError:
                self.send_json({'type':'error', 'message':'You need to select a mission first'})
        else:
            # Otherwise, send this to ourselves as a channels event
            async_to_sync(self.channel_layer.send)(self.channel_name, content);

    def mission_list_get(self, event):
        self.send_json({'type': 'mission.list', 'missions': [
            {'id': launch.id, 'name': launch.name} for launch in Launch.objects.all()
        ]})

    def mission_select(self, event):
        if self.attributes_missing(event, ['id']):
            return

        try:
            launch = Launch.objects.get(pk=event['id'])
        except Launch.DoesNotExist:
            self.send_json({'type':'error', 'message':'Mission does not exist'})
        else:
            self.mission = launch
            async_to_sync(self.channel_layer.group_add)(
                self.layer_group_name_decorate(self.mission.name),
                self.channel_name
            )
            self.send_json({'type':'ack.mission.select'})

    def location_ars(self, event):
        if self.attributes_missing(event, ['lat','lng','alt']):
            return
        self.latitude = event['lat']
        self.longitude = event['lng']
        self.altitude = event['alt']

    def name_ars(self, event):
        if self.attributes_missing(event, ['name']):
            return
        self.name = event['name']

# In routing.py
from channels.routing import route
from .consumers import ws_connect, ws_receive

channel_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.receive", ws_receive),
]

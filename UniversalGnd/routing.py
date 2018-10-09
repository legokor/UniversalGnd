from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter
import tracker.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            tracker.routing.websocket_urlpatterns
        )
    ),
    'channel': ChannelNameRouter(
        tracker.routing.gnd_workers
    )
})

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws', consumers.Consumer),
]
gnd_workers = {
    'upra-gnd': consumers.UpraGndWorker
}

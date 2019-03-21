from django.urls import path

from . import consumers
from . import upra_ars

websocket_urlpatterns = [
    path('ws/client', consumers.Consumer),
    path('ws/upra-ars', upra_ars.UpraArsConsumer),
]
gnd_workers = {
    'upra-gnd': consumers.UpraGndWorker
}

from datetime import datetime, timezone
from asgiref.sync import async_to_sync

from .radio_station import RadioStationConsumer
from .models import Launch

UPRA_TLMPACKET_FMT = (
    r'\$\$(?P<csgn>.{7}),'
    r'(?P<msgid>.{3}),'
    r'(?P<hours>.{2})'
    r'(?P<mins>.{2})'
    r'(?P<secs>.{2}),'
    r'(?P<lat>[+-]?.{2})'
    r'(?P<latmins>.{2}\..{3}),'
    r'(?P<lng>[+-]?.{3})'
    r'(?P<lngmins>.{2}\..{3}),'
    r'(?P<alt>.{5}),'
    r'(?P<exttemp>.{4}),'
    r'(?P<obctemp>.{3}),'
    r'(?P<comtemp>.{3}),'
)

def parse_degrees(degrees_str, mins_str):
    degrees = float(degrees_str)
    mins = float(mins_str)/60.0
    degrees += mins * (-1 if degrees < 0 else 1)
    return degrees

class UpraArsConsumer(RadioStationConsumer):
    """Handles a connection to a radio station using an UPRA modem"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.forwarded_types = ['rawpacket']

    def rawpacket_upra_telemetry(self, event):
        if self.attributes_missing(event, ['packet']):
            return

        match = re.search(UPRA_TLMPACKET_FMT, event['packet'])
        if not match:
            return

        gpshour = int(match.group('hours'))
        gpsminute = int(match.group('mins'))
        gpssecond = int(match.group('secs'))
        gpstime = None

        if gpshour != 33: # The UPRA OBC uses this value if GPS time is not known
            gpstime = datetime.now(timezone.utc).replace(
                hour=gpshour, minute=gpsminute, second=gpssecond)

            # Locations are only valid if we have a GPS fix, and therefore GPS time
            self.send_to_clients({
                'type': 'location.upra',
                'lat': parse_degrees(match.group('lat'), match.group('latmins')),
                'lng': parse_degrees(match.group('lng'), match.group('lngmins')),
                'alt': int(match.group('alt')),
                'tstamp': gpstime.isoformat(timespec='seconds'),
            })

            # Send temperatures
            self.send_to_clients({
                'type': 'temperature.upra',
                'temp': float(match.group('exttemp'))/10.0,
                'obctemp': float(match.group('obctemp'))/10.0,
                'comtemp': float(match.group('comtemp'))/10.0,
                'tstamp': gpstime.isoformat(timespec='seconds')
            })

    def radio_rssi(self, event):
        event['station'] = self.name
        self.send_to_clients(event)

    def ack_upra_gnd_frequnecy_set(self, event):
        event['station'] = self.name
        self.send_to_clients(event)

    def ack_upra_gnd_message_sent(self, event):
        event['station'] = self.name
        self.send_to_clients(event)

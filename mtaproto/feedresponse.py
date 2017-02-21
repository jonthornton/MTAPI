from mtaproto import nyct_subway_pb2
from pytz import timezone
import datetime

_TZ = timezone('US/Eastern')

class FeedResponse(object):

    def __init__(self, response_string):
        self._pb_data = nyct_subway_pb2.gtfs_realtime_pb2.FeedMessage()
        self._pb_data.ParseFromString(response_string)

    def __getattr__(self, name):

        if name == 'timestamp':
            return datetime.datetime.fromtimestamp(self._pb_data.header.timestamp, _TZ)


        return getattr(self._pb_data, name)


class Trip(object):
    def __init__(self, pb_data):
        self._pb_data = pb_data

    def __getattr__(self, name):

        if name == 'direction':
            return self._direction()
        elif name == 'route_id':
            if self._pb_data.trip_update.trip.route_id == 'GS':
                return 'S'
            else:
                return self._pb_data.trip_update.trip.route_id


        return getattr(self._pb_data, name)

    def _direction(self):
        trip_meta = self._pb_data.trip_update.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor]
        return nyct_subway_pb2.NyctTripDescriptor.Direction.Name(trip_meta.direction)

    def is_valid(self):
        return bool(self._pb_data.trip_update)


class TripStop(object):
    def __init__(self, pb_data):
        self._pb_data = pb_data

    def __getattr__(self, name):

        if name == 'time':
            raw_time = self._pb_data.arrival.time or self._pb_data.departure.time
            return datetime.datetime.fromtimestamp(raw_time, _TZ)
        elif name == 'stop_id':
            return str(self._pb_data.stop_id[:3])

        return getattr(self._pb_data, name)

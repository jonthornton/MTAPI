from mtaproto import nyct_subway_pb2

class FeedResponse(object):

    def __init__(self, response_string):
        self._pb_data = nyct_subway_pb2.gtfs_realtime_pb2.FeedMessage()
        self._pb_data.ParseFromString(response_string)

    def __getattr__(self, name):
        return getattr(self._pb_data, name)


class Trip(object):
    def __init__(self, pb_data):
        self._pb_data = pb_data

    def __getattr__(self, name):

        if name == 'direction':
            return self._direction()

        return getattr(self._pb_data, name)

    def _direction(self):
        trip_meta = self._pb_data.trip_update.trip.Extensions[nyct_subway_pb2.nyct_trip_descriptor]
        return nyct_subway_pb2.NyctTripDescriptor.Direction.Name(trip_meta.direction)

    def is_valid(self):
        return bool(self._pb_data.trip_update)

class Update(object):
    def __init__(self, pb_data):
        self._pb_data = pb_data

    def __getattr__(self, name):
        return getattr(self._pb_data, name)

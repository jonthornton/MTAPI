from mtaproto import nyct_subway_pb2

class FeedResponse(object):

    def __init__(self, response_string):
        self._pb_data = nyct_subway_pb2.gtfs_realtime_pb2.FeedMessage()
        self._pb_data.ParseFromString(response_string)


    def __getattr__(self, name):
        return getattr(self._pb_data, name)


class Trip(object):

    pass

class Update(object):
    pass

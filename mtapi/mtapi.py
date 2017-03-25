import urllib2, contextlib, datetime, copy
from collections import defaultdict
from operator import itemgetter
import csv, math, json
import threading
import logging
import google.protobuf.message
from mtaproto.feedresponse import FeedResponse, Trip, TripStop, TZ
from _mtapithreader import _MtapiThreader

logger = logging.getLogger(__name__)

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

class Mtapi(object):

    _FEED_URLS = [
        'http://datamine.mta.info/mta_esi.php?feed_id=1',
        'http://datamine.mta.info/mta_esi.php?feed_id=2',
        'http://datamine.mta.info/mta_esi.php?feed_id=16',
        'http://datamine.mta.info/mta_esi.php?feed_id=21'
    ]

    def __init__(self, key, stations_file, expires_seconds=60, max_trains=10, max_minutes=30, threaded=False):
        self._KEY = key
        self._MAX_TRAINS = max_trains
        self._MAX_MINUTES = max_minutes
        self._EXPIRES_SECONDS = expires_seconds
        self._THREADED = threaded
        self._stations = {}
        self._stops_to_stations = {}
        self._routes = {}
        self._read_lock = threading.RLock()

        self._init_feeds_key(key)

        # initialize the stations database
        try:
            with open(stations_file, 'rb') as f:
                self._stations = json.load(f)
                self._stops_to_stations = self._build_stops_index(self._stations)

        except IOError as e:
            print 'Couldn\'t load stations file '+stations_file
            exit()

        self._update()

        if self._THREADED:
            self.threader = _MtapiThreader(self, expires_seconds)
            self.threader.start_timer()

    def _init_feeds_key(self, key):
        self._FEED_URLS = list(map(lambda x: x + '&key=' + key, self._FEED_URLS))

    @staticmethod
    def _build_stops_index(stations):
        stops = {}
        for station_id in stations:
            for stop_id in stations[station_id]['stops'].keys():
                stops[stop_id] = station_id

        return stops

    @staticmethod
    def _load_mta_feed(feed_url):
        try:
            with contextlib.closing(urllib2.urlopen(feed_url)) as r:
                data = r.read()
                return FeedResponse(data)

        except (urllib2.URLError, google.protobuf.message.DecodeError) as e:
            logger.error('Couldn\'t connect to MTA server: ' + str(e))
            return False

    def _update(self):
        logger.info('updating...')
        self._last_update = datetime.datetime.now(TZ)

        # create working copy for thread safety
        stations = copy.deepcopy(self._stations)

        # clear old times
        for id in stations:
            stations[id]['N'] = []
            stations[id]['S'] = []
            stations[id]['routes'] = set()

        stops = self._build_stops_index(stations)
        routes = defaultdict(set)

        for i, feed_url in enumerate(self._FEED_URLS):
            mta_data = self._load_mta_feed(feed_url)

            if not mta_data:
                continue

            max_time = self._last_update + datetime.timedelta(minutes = self._MAX_MINUTES)

            for entity in mta_data.entity:
                trip = Trip(entity)

                if not trip.is_valid():
                    continue

                direction = trip.direction[0]
                route_id = trip.route_id

                for update in entity.trip_update.stop_time_update:
                    trip_stop = TripStop(update)

                    if trip_stop.time < self._last_update or trip_stop.time > max_time:
                        continue

                    stop_id = trip_stop.stop_id

                    if stop_id not in self._stops_to_stations:
                        logger.info('Stop %s not found', stop_id)
                        continue

                    station_id = self._stops_to_stations[stop_id]
                    stations[station_id]['routes'].add(route_id)
                    stations[station_id][direction].append({
                        'route': route_id,
                        'time': trip_stop.time
                    })

                    routes[route_id].add(stop_id)


        # sort by time
        for id in stations:
            if stations[id]['S'] or stations[id]['N']:
                stations[id]['hasData'] = True
                stations[id]['S'] = sorted(stations[id]['S'], key=itemgetter('time'))[:self._MAX_TRAINS]
                stations[id]['N'] = sorted(stations[id]['N'], key=itemgetter('time'))[:self._MAX_TRAINS]
            else:
                stations[id]['hasData'] = False

        with self._read_lock:
            self._routes = routes
            self._stations = stations

    def last_update(self):
        return self._last_update

    def get_by_point(self, point, limit=5):
        if self.is_expired():
            self._update()

        with self._read_lock:
            sortable_stations = copy.deepcopy(self._stations)

        sortable_stations.sort(key=lambda x: distance(x['location'], point))
        return sortable_stations[:limit]

    def get_routes(self):
        return self._routes.keys()

    def get_by_route(self, route):
        if self.is_expired():
            self._update()

        with self._read_lock:
            out = [ self._stations[self._stops_to_stations[k]] for k in self._routes[route] ]

        out.sort(key=lambda x: x['name'])

        return out

    def get_by_id(self, ids):
        if self.is_expired():
            self._update()

        with self._read_lock:
            out = [ self._stations[k] for k in ids ]

        return out

    def is_expired(self):
        if self.threader and self.threader.restart_if_dead():
            return False
        elif self._EXPIRES_SECONDS:
            age = datetime.datetime.now(TZ) - self._last_update
            return age.total_seconds() > self._EXPIRES_SECONDS
        else:
            return False

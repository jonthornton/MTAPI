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

    class _Station(object):
        last_update = None

        def __init__(self, json):
            self.json = json
            self.trains = {}
            self.clear_train_data()

        def __getitem__(self, key):
            return self.json[key]

        def add_train(self, route_id, direction, train_time, feed_time):
            self.routes.add(route_id)
            self.trains[direction].append({
                'route': route_id,
                'time': train_time
            })
            self.last_update = feed_time

        def clear_train_data(self):
            self.trains['N'] = []
            self.trains['S'] = []
            self.routes = set()
            self.last_update = None

        def sort_trains(self, max_trains):
            self.trains['S'] = sorted(self.trains['S'], key=itemgetter('time'))[:max_trains]
            self.trains['N'] = sorted(self.trains['N'], key=itemgetter('time'))[:max_trains]

        def serialize(self):
            out = {
                'N': self.trains['N'],
                'S': self.trains['S'],
                'routes': self.routes,
                'last_update': self.last_update
            }
            out.update(self.json)
            return out


    _FEED_URLS = [
        'http://datamine.mta.info/mta_esi.php?feed_id=1',  # 123456S
        'http://datamine.mta.info/mta_esi.php?feed_id=2',  # L
        'http://datamine.mta.info/mta_esi.php?feed_id=16', # NRQW
        'http://datamine.mta.info/mta_esi.php?feed_id=21', # BDFM
        'http://datamine.mta.info/mta_esi.php?feed_id=26', # ACE
        'http://datamine.mta.info/mta_esi.php?feed_id=51', # 7
        'http://datamine.mta.info/mta_esi.php?feed_id=36', # JZ
        'http://datamine.mta.info/mta_esi.php?feed_id=31'  # G
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

        self._FEED_URLS = self._init_feeds_key(key, self._FEED_URLS)

        # initialize the stations database
        try:
            with open(stations_file, 'rb') as f:
                self._stations = json.load(f)
                for id in self._stations:
                    self._stations[id] = self._Station(self._stations[id])
                self._stops_to_stations = self._build_stops_index(self._stations)

        except IOError as e:
            print 'Couldn\'t load stations file '+stations_file
            exit()

        self._update()

        if threaded:
            self.threader = _MtapiThreader(self, expires_seconds)
            self.threader.start_timer()

    @staticmethod
    def _init_feeds_key(key, urls):
        return list(map(lambda x: x + '&key=' + key, urls))

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
            stations[id].clear_train_data()

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
                    stations[station_id].add_train(route_id,
                                                   direction,
                                                   trip_stop.time,
                                                   mta_data.timestamp)

                    routes[route_id].add(stop_id)


        # sort by time
        for id in stations:
            stations[id].sort_trains(self._MAX_TRAINS)

        with self._read_lock:
            self._routes = routes
            self._stations = stations

    def last_update(self):
        return self._last_update

    def get_by_point(self, point, limit=5):
        if self.is_expired():
            self._update()

        with self._read_lock:
            sortable_stations = copy.deepcopy(self._stations).values()

        sortable_stations.sort(key=lambda x: distance(x['location'], point))
        sortable_stations = map(lambda x: x.serialize(), sortable_stations)
        return sortable_stations[:limit]

    def get_routes(self):
        return self._routes.keys()

    def get_by_route(self, route):
        if self.is_expired():
            self._update()

        with self._read_lock:
            out = [ self._stations[self._stops_to_stations[k]].serialize() for k in self._routes[route] ]

        out.sort(key=lambda x: x['name'])
        return out

    def get_by_id(self, ids):
        if self.is_expired():
            self._update()

        with self._read_lock:
            out = [ self._stations[k].serialize() for k in ids ]

        return out

    def is_expired(self):
        if self._THREADED and self.threader and self.threader.restart_if_dead():
            return False
        elif self._EXPIRES_SECONDS:
            age = datetime.datetime.now(TZ) - self._last_update
            return age.total_seconds() > self._EXPIRES_SECONDS
        else:
            return False

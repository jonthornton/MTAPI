import gtfs_realtime_pb2, nyct_subway_pb2
import urllib2, contextlib, datetime, copy
from operator import itemgetter
from pytz import timezone
import threading, time
import csv, math, json
import logging
import google.protobuf.message

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

class MtaSanitizer(object):

    _last_update = 0
    _tz = timezone('US/Eastern')

    def __init__(self, key, stations_file, expires_seconds=None, max_trains=10, max_minutes=30, threaded=False):
        self._KEY = key
        self._MAX_TRAINS = max_trains
        self._MAX_MINUTES = max_minutes
        self._EXPIRES_SECONDS = expires_seconds
        self._THREADED = threaded
        self._stations = []
        self._stops = {}
        self._routes = {}
        self._read_lock = threading.RLock()
        self._update_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # initialize the stations database
        try:
            with open(stations_file, 'rb') as f:
                self._stations = json.load(f)
                for idx, station in enumerate(self._stations):
                    station['id'] = idx

        except IOError as e:
            print 'Couldn\'t load stations file '+stations_file
            exit()

        self._update()

        if self._THREADED:
            self._start_timer()

    def _start_timer(self):
        self.logger.info('Starting update thread...')
        self._timer_thread = threading.Thread(target=self._update_timer)
        self._timer_thread.daemon = True
        self._timer_thread.start()

    def _update_timer(self):
        while True:
            time.sleep(self._EXPIRES_SECONDS)
            self._update_thread = threading.Thread(target=self._update)
            self._update_thread.start()

    @staticmethod
    def _build_stops_index(stations):
        stops = {}
        for station in stations:
            for stop_id in station['stops'].keys():
                stops[stop_id] = station

        return stops

    def _update(self):
        if not self._update_lock.acquire(False):
            self.logger.info('update locked!')
            return

        self.logger.info('updating...')

        # create working copy for thread safety
        stations = copy.deepcopy(self._stations)

        # clear old times
        for station in stations:
            station['N'] = []
            station['S'] = []
            station['routes'] = set()

        stops = MtaSanitizer._build_stops_index(stations)
        routes = {}

        feed_urls = [
            'http://datamine.mta.info/mta_esi.php?feed_id=1&key='+self._KEY,
            'http://datamine.mta.info/mta_esi.php?feed_id=2&key='+self._KEY
        ]

        for i, feed_url in enumerate(feed_urls):
            mta_data = gtfs_realtime_pb2.FeedMessage()
            try:
                with contextlib.closing(urllib2.urlopen(feed_url)) as r:
                    data = r.read()
                    mta_data.ParseFromString(data)

            except (urllib2.URLError, google.protobuf.message.DecodeError) as e:
                self.logger.error('Couldn\'t connect to MTA server: ' + str(e))
                self._update_lock.release()
                return

            self._last_update = datetime.datetime.fromtimestamp(mta_data.header.timestamp, self._tz)
            self._MAX_TIME = self._last_update + datetime.timedelta(minutes = self._MAX_MINUTES)

            for entity in mta_data.entity:
                if entity.trip_update:
                    for update in entity.trip_update.stop_time_update:
                        time = update.arrival.time
                        if time == 0:
                            time = update.departure.time

                        time = datetime.datetime.fromtimestamp(time, self._tz)
                        if time < self._last_update or time > self._MAX_TIME:
                            continue

                        route_id = entity.trip_update.trip.route_id
                        if route_id == 'GS':
                            route_id = 'S'

                        stop_id = str(update.stop_id[:3])
                        station = stops[stop_id]
                        direction = update.stop_id[3]

                        station[direction].append({
                            'route': route_id,
                            'time': time
                        })

                        station['routes'].add(route_id)
                        try:
                            routes[route_id].add(stop_id)
                        except KeyError, e:
                            routes[route_id] = set([stop_id])



        # sort by time
        for station in stations:
            if station['S'] or station['N']:
                station['hasData'] = True
                station['S'] = sorted(station['S'], key=itemgetter('time'))[:self._MAX_TRAINS]
                station['N'] = sorted(station['N'], key=itemgetter('time'))[:self._MAX_TRAINS]
            else:
                station['hasData'] = False

        with self._read_lock:
            self._stops = stops
            self._routes = routes
            self._stations = stations

        self._update_lock.release()

    def last_update(self):
        return self._last_update

    def get_by_point(self, point, limit=5):
        if self.is_expired():
            self.update()

        with self._read_lock:
            sortable_stations = copy.deepcopy(self._stations)

        sortable_stations.sort(key=lambda x: distance(x['location'], point))
        return sortable_stations[:limit]

    def get_routes(self):
        return self._routes.keys()

    def get_by_route(self, route):
        if self.is_expired():
            self.update()

        with self._read_lock:
            out = [ self._stops[k] for k in self._routes[route] ]

        out.sort(key=lambda x: x['name'])

        return out

    def get_by_id(self, ids):
        if self.is_expired():
            self.update()

        with self._read_lock:
            out = [ self._stations[k] for k in ids ]

        return out

    def is_expired(self):
        if self._THREADED:
            # check that the update thread is still running
            if not self._timer_thread.is_alive():
                self._start_timer()
                return False

        elif self._EXPIRES_SECONDS:
            age = datetime.datetime.now(self._tz) - self._last_update
            return age.total_seconds() > self._EXPIRES_SECONDS
        else:
            return False

import gtfs_realtime_pb2, nyct_subway_pb2
import urllib2, contextlib, datetime, copy
from operator import itemgetter
from pprint import pprint
from pytz import timezone
import threading, time
import csv, math
import logging

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

class MtaSanitizer(object):

    _last_update = 0
    _tz = timezone('US/Eastern')

    def __init__(self, key, stops_file, expires_seconds=None, max_trains=10, max_minutes=30, threaded=False):
        self._KEY = key
        self._MAX_TRAINS = max_trains
        self._MAX_MINUTES = max_minutes
        self._EXPIRES_SECONDS = expires_seconds
        self._THREADED = threaded
        self._stations = []
        self._stops = {}
        self._routes = {}
        self._read_lock = threading.Lock()
        self._update_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # initialize the stations database
        with open(stops_file, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['parent_station']:
                    continue

                stop = {
                    'id': str(row['stop_id']),
                    'name': row['stop_name'],
                    'location': (float(row['stop_lat']), float(row['stop_lon']))
                }

                self._group_stop(stop)

        for station in self._stations:
            # TODO: improve name grouping
            station['name'] = ' / '.join(station['name'])

        self._update()

        if self._THREADED:
            self._thread = threading.Thread(target=self._threaded_update)
            self._thread.daemon = True
            self._thread.start()

    def _threaded_update(self):
        while True:
            time.sleep(self._EXPIRES_SECONDS)
            self._update()

    @staticmethod
    def _build_stops_index(stations):
        stops = {}
        for station in stations:
            for stop_id in station['stops'].keys():
                stops[stop_id] = station

        return stops

    def _group_stop(self, stop):
        GROUPING_THRESHOLD = 0.003

        # this is O(n^2) - can definitely be improved
        for station in self._stations:
            if distance(stop['location'], station['location']) < GROUPING_THRESHOLD:
                station['name'].add(stop['name'])
                station['stops'][stop['id']] = stop['location']
                new_lat = sum(v[0] for v in station['stops'].values()) / float(len(station['stops']))
                new_lon = sum(v[1] for v in station['stops'].values()) / float(len(station['stops']))
                station['location'] = (new_lat, new_lon)
                return

        station = {
            'name': set([stop['name']]),
            'location': stop['location'],
            'stops': { stop['id']: stop['location'] },
            'N': [],
            'S': []
        }
        self._stations.append(station)


    def _update(self):
        if not self._update_lock.acquire(False):
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
            except URLError, e:
                self.logger.error('Couldn\'t connect to MTA server. Code '+str(e.code))
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
            out = {k: self._stops[k] for k in self._routes[route]}

        return out

    def is_expired(self):
        if not self._THREADED and self._EXPIRES_SECONDS:
            age = datetime.datetime.now(self._tz) - self._last_update
            return age.total_seconds() > self._EXPIRES_SECONDS
        else:
            return False

import gtfs_realtime_pb2, nyct_subway_pb2
import urllib2, contextlib, time, datetime, copy
from operator import itemgetter
from pprint import pprint
from pytz import timezone
import threading, atexit
import csv, math

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

        self.update()

        if self._THREADED:
            self._update_lock = threading.Lock()
            self._thread = threading.Thread(target=self._threaded_update)
            self._thread.daemon = True
            self._thread.start()

    def _threaded_update(self):
        while True:
            time.sleep(self._EXPIRES_SECONDS)
            print '_threaded_update'
            self._update_lock.acquire()
            self.update()
            self._update_lock.release()

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
                self._stops[stop['id']] = station
                return

        station = {
            'name': set([stop['name']]),
            'location': stop['location'],
            'stops': { stop['id']: stop['location'] },
            'N': [],
            'S': []
        }
        self._stations.append(station)
        self._stops[stop['id']] = station


    def update(self):
        print 'updating...'
        # clear old times
        for station in self._stations:
            station['N'] = []
            station['S'] = []
            station['routes'] = set()

        feed_urls = [
            'http://datamine.mta.info/mta_esi.php?feed_id=1&key='+self._KEY,
            'http://datamine.mta.info/mta_esi.php?feed_id=2&key='+self._KEY
        ]

        for i, feed_url in enumerate(feed_urls):
            mta_data = gtfs_realtime_pb2.FeedMessage()
            with contextlib.closing(urllib2.urlopen(feed_url)) as r:
                data = r.read()
                mta_data.ParseFromString(data)

            self._last_update = datetime.datetime.fromtimestamp(mta_data.header.timestamp, self._tz)
            self._MAX_TIME = self._last_update + datetime.timedelta(minutes = self._MAX_MINUTES)

            self._process_feed(mta_data)

        # sort by time
        for station in self._stations:
            if station['S'] or station['N']:
                station['hasData'] = True
                station['S'] = sorted(station['S'], key=itemgetter('time'))[:self._MAX_TRAINS]
                station['N'] = sorted(station['N'], key=itemgetter('time'))[:self._MAX_TRAINS]
            else:
                station['hasData'] = False

    def last_update(self):
        return self._last_update

    def get_by_point(self, point, limit=5):
        if self.is_expired():
            self.update()

        sortable_stations = copy.copy(self._stations)
        sortable_stations.sort(key=lambda x: distance(x['location'], point))
        return sortable_stations[:limit]

    def get_routes(self):
        return self._routes.keys()

    def get_by_route(self, route):
        if self.is_expired():
            self.update()

        return {k: self._stops[k] for k in self._routes[route]}

    def is_expired(self):
        if not self._THREADED and self._EXPIRES_SECONDS:
            age = datetime.datetime.now(self._tz) - self._last_update
            return age.total_seconds() > self._EXPIRES_SECONDS
        else:
            return False

    def _process_feed(self, rawData):
        for entity in rawData.entity:
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
                    station = self._stops[stop_id]
                    direction = update.stop_id[3]

                    station[direction].append({
                        'route': route_id,
                        'time': time
                    })

                    station['routes'].add(route_id)

                    try:
                        self._routes[route_id].add(stop_id)
                    except KeyError, e:
                        self._routes[route_id] = set([stop_id])


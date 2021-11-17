import urllib, contextlib, datetime, copy
from collections import defaultdict
from itertools import islice
from operator import itemgetter
import csv, math, json
import threading
import logging
import google.protobuf.message
from mtaproto.feedresponse import FeedResponse, Trip, TripStop, TZ, BusTrip, BusTripStop
from mtapi._mtapithreader import _MtapiThreader

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
            self.alerts = {}

        def __getitem__(self, key):
            return self.json[key]

        def add_train(self, route_id, direction, train_time, feed_time):
            self.routes.add(route_id)
            self.trains[direction].append({
                'route': route_id,
                'time': train_time
            })
            self.last_update = feed_time

        def add_alert(self, alert, id):
            try:
                parsed_id = id.split('#')[1]
            except IndexError:
                parsed_id = id

            if parsed_id not in self.alerts.keys():
                alert_instance = dict()
                alert_instance['header'] = alert.header_text.translation[0].text
                for translation in alert.description_text.translation:
                    alert_instance[translation.language] = translation.text
                alert_instance['last_update'] = self.last_update
                self.alerts[parsed_id] = alert_instance

        def clear_alerts(self):
            self.alerts = {}

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

    class _BusStation(object):
        last_update = None

        def __init__(self, json):
            self.json = json
            self.trains = {}
            self.clear_train_data()
            self.alerts = {}

        def __getitem__(self, key):
            return self.json[key]

        def add_train(self, route_id, direction, train_time, feed_time):
            self.routes.add(route_id)
            self.trains[direction].append({
                'route': route_id,
                'time': train_time
            })
            self.last_update = feed_time

        def add_alert(self, alert, id):
            try:
                parsed_id = id.split('#')[1]
            except IndexError:
                parsed_id = id

            if parsed_id not in self.alerts.keys():
                alert_instance = dict()
                alert_instance['header'] = alert.header_text.translation[0].text
                for translation in alert.description_text.translation:
                    alert_instance[translation.language] = translation.text
                alert_instance['last_update'] = self.last_update
                self.alerts[parsed_id] = alert_instance

        def clear_alerts(self):
            self.alerts = {}


        def clear_train_data(self):
            self.trains['1'] = []
            self.trains['0'] = []
            self.routes = set()
            self.last_update = None

        def sort_trains(self, max_trains):
            self.trains['1'] = sorted(self.trains['1'], key=itemgetter('time'))[:max_trains]
            self.trains['0'] = sorted(self.trains['0'], key=itemgetter('time'))[:max_trains]

        def serialize(self):
            out = {
                '1': self.trains['1'],
                '0': self.trains['0'],
                'routes': self.routes,
                'last_update': self.last_update
            }
            out.update(self.json)
            return out


    _FEED_URLS = [ # ACE, BDFM, G, JZ, NQRW, L, 1234567, SIR
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace',
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm',
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g',
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz',
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw',
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si'
    ]
    _TRAIN_ALERT_FEED_URL = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts'

    _BUS_FEED_URL = ['http://gtfsrt.prod.obanyc.com/tripUpdates']

    _BUS_ALERT_FEED_URL = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fbus-alerts'

    def __init__(self, key, stations_file, bus_stations_file, expires_seconds=60, max_trains=10, max_minutes=30, threaded=False):
        self._KEY = key
        self._MAX_TRAINS = max_trains
        self._MAX_MINUTES = max_minutes
        self._EXPIRES_SECONDS = expires_seconds
        self._THREADED = threaded
        self._stations = {}
        self._stops_to_stations = {}
        self._routes = {}
        self._read_lock = threading.RLock()

        # bus elements
        self._bus_stations = {}
        self._bus_stops_to_stations = {}
        self._bus_routes = {}

        # initialize the stations database
        try:
            with open(stations_file, 'rb') as f:
                self._stations = json.load(f)
                for id in self._stations:
                    self._stations[id] = self._Station(self._stations[id])
                self._stops_to_stations = self._build_stops_index(self._stations)

        except IOError as e:
            print('Couldn\'t load stations file '+stations_file)
            exit()

        # initialize the bus stations database
        try:
            with open(bus_stations_file, 'rb') as f:
                self._bus_stations = json.load(f)
                for id in self._bus_stations:
                    self._bus_stations[id] = self._BusStation(self._bus_stations[id])
                self._bus_stops_to_stations = self._build_stops_index(self._bus_stations)
        except IOError as e:
            print('Couldn\'t load stations file ' + stations_file)
            exit()

        self._update()
        self._bus_update()

        if threaded:
            self.threader = _MtapiThreader(self, expires_seconds)
            self.threader.start_timer()

    @staticmethod
    def _build_stops_index(stations):
        stops = {}
        for station_id in stations:
            for stop_id in stations[station_id]['stops'].keys():
                stops[stop_id] = station_id

        return stops

    def _load_mta_feed(self, feed_url):
        try:
            request = urllib.request.Request(feed_url)
            request.add_header('x-api-key', self._KEY)
            with contextlib.closing(urllib.request.urlopen(request)) as r:
                data = r.read()
                return FeedResponse(data)

        except (urllib.error.URLError, google.protobuf.message.DecodeError, ConnectionResetError) as e:
            logger.error('Couldn\'t connect to MTA server: ' + str(e))
            return False

    def _update(self):
        logger.info('updating trains...')
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
                route_id = trip.route_id.upper()

                for update in entity.trip_update.stop_time_update:
                    trip_stop = TripStop(update)

                    if trip_stop.time < self._last_update or trip_stop.time > max_time:
                        continue

                    stop_id = trip_stop.stop_id

                    if stop_id not in self._stops_to_stations:
                        # No need to print error message for non-existing stop
                        # logger.info('Stop %s not found', stop_id)
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

        stations = self._train_alert(stations)

        with self._read_lock:
            self._routes = routes
            self._stations = stations

    def _bus_update(self):
        logger.info('updating bus...')
        self._bus_last_update = datetime.datetime.now(TZ)

        # create working copy for thread safety
        stations = copy.deepcopy(self._bus_stations)

        # clear old times
        for id in stations:
            stations[id].clear_train_data()

        routes = defaultdict(set)

        for i, feed_url in enumerate(self._BUS_FEED_URL):
            mta_data = self._load_mta_feed(feed_url)

            if not mta_data:
                continue

            max_time = self._bus_last_update + datetime.timedelta(minutes=self._MAX_MINUTES)

            for entity in mta_data.entity:
                trip = BusTrip(entity)

                if not trip.is_valid():
                    continue

                direction = trip.direction[0]
                route_id = trip.route_id.upper()

                for update in entity.trip_update.stop_time_update:
                    trip_stop = BusTripStop(update)

                    if trip_stop.time < self._bus_last_update or trip_stop.time > max_time:
                        continue

                    stop_id = trip_stop.stop_id

                    if stop_id not in self._bus_stops_to_stations:
                        # No need to print error message for non-existing stop
                        # logger.info('Stop %s not found', stop_id)
                        continue

                    station_id = self._bus_stops_to_stations[stop_id]
                    stations[station_id].add_train(route_id,
                                                   direction,
                                                   trip_stop.time,
                                                   mta_data.timestamp)

                    routes[route_id].add(stop_id)

        # sort by time
        for id in stations:
            stations[id].sort_trains(self._MAX_TRAINS)

        stations = self._bus_alert(stations)

        with self._read_lock:
            self._bus_routes = routes
            self._bus_stations = stations


    def _train_alert(self, stations):
        logger.info("updating train alerts...")

        # clear previous alerts to ensure we have the most up to date data
        for station in stations.values():
            station.clear_alerts()

        self._train_alert_last_update = datetime.datetime.now(TZ)
        mta_data = self._load_mta_feed(self._TRAIN_ALERT_FEED_URL)

        if not mta_data:
            return

        for entity in mta_data.entity:
            for informed_entity in entity.alert.informed_entity:
                if informed_entity.stop_id:
                    try:
                        stations[self._stops_to_stations[informed_entity.stop_id]].add_alert(entity.alert, entity.id)
                    except KeyError as e:
                        try:
                            stations[self._stops_to_stations[informed_entity.stop_id[:-1]]].add_alert(entity.alert, entity.id)
                        except KeyError as e1:
                            logger.error("{0} stop does not exist. Might need to update stations file.".format(informed_entity.stop_id))

        return stations


    def _bus_alert(self, stations):
        logger.info("updating bus alerts...")

        # clear previous alerts to ensure we have the most up to date data
        for station in stations.values():
            station.clear_alerts()

        self._bus_alert_last_update = datetime.datetime.now(TZ)
        mta_data = self._load_mta_feed(self._BUS_ALERT_FEED_URL)

        if not mta_data:
            return

        for entity in mta_data.entity:
            for informed_entity in entity.alert.informed_entity:
                if informed_entity.stop_id:
                    try:
                        stations[self._bus_stops_to_stations[informed_entity.stop_id]].add_alert(entity.alert, entity.id)
                    except KeyError as e:
                        try:
                            stations[self._bus_stops_to_stations[informed_entity.stop_id[:-1]]].add_alert(entity.alert,
                                                                                                      entity.id)
                        except KeyError as e1:
                            logger.error("{0} stop does not exist. Might need to update stations file.".format(
                                informed_entity.stop_id))

        return stations


    def last_update(self):
        return self._last_update

    def bus_last_update(self):
        return self._bus_last_update

    def get_by_point(self, point, limit=5):
        if self.is_expired():
            self._update()

        with self._read_lock:
            sortable_stations = copy.deepcopy(self._stations).values()

        sorted_stations = sorted(sortable_stations, key=lambda s: distance(s['location'], point))
        serialized_stations = map(lambda s: s.serialize(), sorted_stations)

        return list(islice(serialized_stations, limit))

    def bus_get_by_point(self, point, limit=5):
        if self.is_expired():
            self._bus_update()

        with self._read_lock:
            sortable_stations = copy.deepcopy(self._bus_stations).values()

        sorted_stations = sorted(sortable_stations, key=lambda s: distance(s['location'], point))
        serialized_stations = map(lambda s: s.serialize(), sorted_stations)

        return list(islice(serialized_stations, limit))

    def get_routes(self):
        return self._routes.keys()

    def bus_get_routes(self):
        return self._bus_routes.keys()

    def get_by_route(self, route):
        route = route.upper()

        if self.is_expired():
            self._update()

        with self._read_lock:
            out = [ self._stations[self._stops_to_stations[k]].serialize() for k in self._routes[route] ]

        out.sort(key=lambda x: x['name'])
        return out

    def bus_get_by_route(self, route):
        route = route.upper()

        if self.is_expired():
            self._bus_update()

        with self._read_lock:
            out = [self._bus_stations[self._bus_stops_to_stations[k]].serialize() for k in self._bus_routes[route]]

        out.sort(key=lambda x: x['name'])
        return out

    def get_by_id(self, ids):
        if self.is_expired():
            self._update()

        with self._read_lock:
            out = [ self._stations[k].serialize() for k in ids ]

        return out

    def bus_get_by_id(self, ids):
        if self.is_expired():
            self._bus_update()

        with self._read_lock:
            out = [ self._bus_stations[k].serialize() for k in ids ]

        return out

    def train_get_alert_by_stop(self, stopid):
        stopid = stopid.upper()
        if self.is_expired():
            self._update()

        with self._read_lock:
            out = self._stations[self._stops_to_stations[stopid]].alerts.values()

        return out


    def train_get_alerts_route(self, route):
        route = route.upper()

        if self.is_expired():
            self._bus_update()

        with self._read_lock:

            out = [{self._stops_to_stations[k]: self._stations[self._stops_to_stations[k]].alerts.values()} for k in self._routes[route] if len(self._stations[self._stops_to_stations[k]].alerts.values()) > 0]

        return out


    def is_expired(self):
        if self._THREADED and self.threader and self.threader.restart_if_dead():
            return False
        elif self._EXPIRES_SECONDS:
            age = datetime.datetime.now(TZ) - self._last_update
            return age.total_seconds() > self._EXPIRES_SECONDS
        else:
            return False

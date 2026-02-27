import urllib, contextlib, datetime, copy
from collections import defaultdict
from itertools import islice
from operator import itemgetter
import csv, math, json
import threading
import logging
import google.protobuf.message
from mtaproto.feedresponse import FeedResponse, Trip, TripStop, TZ
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
            self.alerts = []

        def __getitem__(self, key):
            return self.json[key]

        def add_train(self, route_id, direction, train_time, feed_time):
            self.routes.add(route_id)
            self.trains[direction].append({
                'route': route_id,
                'time': train_time
            })
            self.last_update = feed_time
        
        def add_alert(self, alert_type, alert_text):
            # Only add alerts once
            if not any(a['header_text'] == alert_text for a in self.alerts):
                self.alerts.append({
                    'type': alert_type,
                    'header_text': alert_text
                })

        def clear_train_data(self):
            self.trains['N'] = []
            self.trains['S'] = []
            self.routes = set()
            self.last_update = None
            self.alerts = []

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
            if self.alerts:
                out['service_alerts'] = self.alerts # Only add service alerts if they exist
            out.update(self.json)
            return out


    _FEED_URLS = [
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs',  # 1234567S
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',  # L
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw', # NRQW
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm', # BDFM
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace', # ACE
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si', # (SIR)
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz', # JZ
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'  # G
    ]

    # GTFS feed for subway service alerts
    _SERVICE_ALERT_URL = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts'

    def __init__(self, stations_file, expires_seconds=60, max_trains=10, max_minutes=30, threaded=False, service_alerts=False):
        self._MAX_TRAINS = max_trains
        self._MAX_MINUTES = max_minutes
        self._EXPIRES_SECONDS = expires_seconds
        self._THREADED = threaded
        self._GET_SERVICE_ALERTS = service_alerts
        self._stations = {}
        self._stops_to_stations = {}
        self._routes = {}
        self._read_lock = threading.RLock()

        # initialize the stations database
        try:
            with open(stations_file, 'r') as f:
                self._stations = json.load(f)
                for id in self._stations:
                    self._stations[id] = self._Station(self._stations[id])
                self._stops_to_stations = self._build_stops_index(self._stations)

        except IOError as e:
            print('Couldn\'t load stations file '+stations_file)
            exit()

        self._update()

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
            with contextlib.closing(urllib.request.urlopen(request)) as r:
                data = r.read()
                return FeedResponse(data)

        except (urllib.error.URLError, google.protobuf.message.DecodeError, ConnectionResetError) as e:
            logger.error('Couldn\'t connect to MTA server: ' + str(e))
            return False
        
    def _is_alert_currently_active(self, entity, current_timestamp: int):
        for period in entity.alert.active_period:
            # Alert is active if current time is within the period
            if period.start <= current_timestamp and (not period.end or period.end >= current_timestamp):
                return True
        return False
    
    def _get_alert_text(self, entity, language='en'):
        # Fall back to 'en' when language isn't available.
        # This is needed for elevator alerts, some text is 
        # better than no text in this case.
        english_text = None
        for translation in entity.alert.header_text.translation:
            if translation.language == language:
                return translation.text
            elif translation.language == 'en':
                english_text = translation.text 
        return english_text
            
    def _get_station_routes(self, station):
        return {
            train['route'] 
            for direction in station.trains.values() 
            for train in direction
        }
    
    def _alert_applies_to_stop(self, informed, station_stops):
        if not informed.HasField('stop_id'):
            return False
        
        # Check both with and without direction suffix (N/S)
        alert_stop = informed.stop_id
        alert_stop_base = alert_stop.rstrip('NS')
        
        return any(stop in [alert_stop, alert_stop_base] for stop in station_stops)

    def _update(self):
        logger.info('updating...')
        self._last_update = datetime.datetime.now(TZ)

        # create working copy for thread safety
        stations = copy.deepcopy(self._stations)

        # clear old times
        for id in stations:
            stations[id].clear_train_data()

        routes = defaultdict(set)

        # Get service alerts
        service_alerts = []
        if self._GET_SERVICE_ALERTS:
            logger.info('fetching service alerts...')
            service_alerts_feed = self._load_mta_feed(self._SERVICE_ALERT_URL)

            if service_alerts_feed:
                # Filter for active alerts
                current_timestamp = int(self._last_update.timestamp())
                service_alerts = [
                    entity for entity in service_alerts_feed.entity
                    if self._is_alert_currently_active(entity, current_timestamp)
                ]

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

        # Add service alerts to stations
        if self._GET_SERVICE_ALERTS and service_alerts:
            for station_id, station in stations.items():
                station_routes = self._get_station_routes(station)

                for alert_entity in service_alerts:
                    alert_text = self._get_alert_text(alert_entity, 'en-html')
                    if not alert_text:
                        continue

                    for informed in alert_entity.alert.informed_entity:
                        # Check if alert applies to this specific stop
                        if self._alert_applies_to_stop(informed, station['stops']):
                            station.add_alert('stop', alert_text)
                            break # Only add once per alert per station

                        # Check if alert applies to a route serving the station
                        if informed.HasField('route_id') and informed.route_id in station_routes:
                            station.add_alert('route', alert_text)
                            break # Only add once per alert per station

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

        sorted_stations = sorted(sortable_stations, key=lambda s: distance(s['location'], point))
        serialized_stations = map(lambda s: s.serialize(), sorted_stations)

        return list(islice(serialized_stations, limit))

    def get_routes(self):
        return self._routes.keys()

    def get_by_route(self, route):
        route = route.upper()

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

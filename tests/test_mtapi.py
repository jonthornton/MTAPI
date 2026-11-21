from mtapi.mtapi import Mtapi

def test_init():
    from app import app
    mta = Mtapi(
        app.config['STATIONS_FILE'],
        max_trains=app.config['MAX_TRAINS'],
        max_minutes=app.config['MAX_MINUTES'],
        expires_seconds=app.config['CACHE_SECONDS'],
        threaded=app.config['THREADED'])

def _station(trains):
    station = Mtapi._Station({'id': 'A17', 'name': 'Test St'})
    for route, direction, time in trains:
        station.add_train(route, direction, time, None)
    station.sort_trains()
    return station

def _times(trains):
    return [t['time'] for t in trains]

TRAINS = [('A', 'N', 1), ('C', 'N', 2), ('A', 'N', 3), ('C', 'S', 4), ('A', 'S', 5)]

def test_serialize_no_filters():
    out = _station(TRAINS).serialize(10)
    assert _times(out['N']) == [1, 2, 3]
    assert _times(out['S']) == [4, 5]

def test_serialize_max_trains():
    out = _station(TRAINS).serialize(2)
    assert _times(out['N']) == [1, 2]
    assert _times(out['S']) == [4, 5]

def test_serialize_route_ids():
    out = _station(TRAINS).serialize(10, route_ids={'C'})
    assert _times(out['N']) == [2]
    assert _times(out['S']) == [4]

def test_serialize_direction():
    out = _station(TRAINS).serialize(10, direction='N')
    assert _times(out['N']) == [1, 2, 3]
    assert out['S'] == []

def test_serialize_combined():
    out = _station(TRAINS).serialize(1, route_ids={'A'}, direction='S')
    assert out['N'] == []
    assert _times(out['S']) == [5]

def test_serialize_filters_before_max_trains():
    trains = [('A', 'N', i) for i in range(12)] + [('C', 'N', 12)]
    out = _station(trains).serialize(10, route_ids={'C'})
    assert _times(out['N']) == [12]

def test_serialize_does_not_modify_station():
    station = _station(TRAINS)
    station.serialize(1, route_ids={'C'}, direction='N')
    assert _times(station.trains['N']) == [1, 2, 3]
    assert _times(station.trains['S']) == [4, 5]

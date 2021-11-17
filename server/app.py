# coding: utf-8
"""
    mta-api-sanity
    ~~~~~~

    Expose the MTA's real-time subway feed as a json api

    :copyright: (c) 2014 by Jon Thornton.
    :license: BSD, see LICENSE for more details.
"""

from mtapi.mtapi import Mtapi
from flask import Flask, request, jsonify, render_template, abort, redirect
from flask.json import JSONEncoder
from flask_cors import CORS
from datetime import datetime
from functools import wraps, reduce
import logging
import os

app = Flask(__name__)
CORS(app)
app.config.update(
    MAX_TRAINS=10,
    MAX_MINUTES=30,
    CACHE_SECONDS=60,
    THREADED=True
)

_SETTINGS_ENV_VAR = 'MTAPI_SETTINGS'
_SETTINGS_DEFAULT_PATH = './settings.cfg'
if _SETTINGS_ENV_VAR in os.environ:
    app.config.from_envvar(_SETTINGS_ENV_VAR)
elif os.path.isfile(_SETTINGS_DEFAULT_PATH):
    app.config.from_pyfile(_SETTINGS_DEFAULT_PATH)
else:
    raise Exception('No configuration found! Create a settings.cfg file or set MTAPI_SETTINGS env variable.')

# set debug logging
if app.debug:
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
app.json_encoder = CustomJSONEncoder

mta = Mtapi(
    app.config['MTA_KEY'],
    app.config['STATIONS_FILE'],
    app.config['BUS_STATIONS_FILE'],
    max_trains=app.config['MAX_TRAINS'],
    max_minutes=app.config['MAX_MINUTES'],
    expires_seconds=app.config['CACHE_SECONDS'],
    threaded=app.config['THREADED'])

'''
def cross_origin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = f(*args, **kwargs)

        if app.config['DEBUG']:
            resp.headers['Access-Control-Allow-Origin'] = '*'
        elif 'CROSS_ORIGIN' in app.config:
            resp.headers['Access-Control-Allow-Origin'] = app.config['CROSS_ORIGIN']

        return resp

    return decorated_function
'''

@app.route('/')
#@cross_origin
def index():
    return jsonify({
        'title': 'MTAPI',
        'readme': 'Visit https://github.com/jonthornton/MTAPI for more info'
        })

@app.route('/by-location', methods=['GET', 'POST'])
#@cross_origin
def by_location():
    try:
        location = (float(request.args['lat']), float(request.args['lon']))
        num_stations = int(request.args['num'])
    except KeyError as e:
        print(e)
        response = jsonify({
            'error': 'Missing lat/lon/num parameter'
            })
        response.status_code = 400
        return response

    data = mta.get_by_point(location, num_stations)
    return _make_envelope(data)

@app.route('/bus/by-location', methods=['GET', 'POST'])
#@cross_origin
def bus_by_location():
    try:
        location = (float(request.args['lat']), float(request.args['lon']))
        num_stations = int(request.args['num'])
    except KeyError as e:
        print(e)
        response = jsonify({
            'error': 'Missing lat/lon/num parameter'
            })
        response.status_code = 400
        return response

    data = mta.bus_get_by_point(location, num_stations)
    return _make_envelope(data)

@app.route('/by-route/<route>', methods=['GET', 'POST'])
#@cross_origin
def by_route(route):

    if route.islower():
        return redirect(request.host_url + 'by-route/' + route.upper(), code=301)

    try:
        data = mta.get_by_route(route)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)


@app.route('/bus/by-route/<route>', methods=['GET', 'POST'])
#@cross_origin
def bus_by_route(route):

    if route.islower():
        return redirect(request.host_url + 'by-route/' + route.upper(), code=301)

    try:
        data = mta.bus_get_by_route(route)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)

@app.route('/by-id/<id_string>', methods=['GET', 'POST'])
#@cross_origin
def by_index(id_string):
    ids = id_string.split(',')
    try:
        data = mta.get_by_id(ids)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)

@app.route('/bus/by-id/<id_string>', methods=['GET', 'POST'])
#@cross_origin
def bus_by_index(id_string):
    ids = id_string.split(',')
    try:
        data = mta.bus_get_by_id(ids)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)

@app.route('/routes', methods=['GET', 'POST'])
#@cross_origin
def routes():
    return jsonify({
        'data': sorted(mta.get_routes()),
        'updated': mta.last_update()
        })

@app.route('/bus/routes', methods=['GET', 'POST'])
#@cross_origin
def bus_routes():
    return jsonify({
        'data': sorted(mta.bus_get_routes()),
        'updated': mta.bus_last_update()
        })

@app.route('/alert-by-stop/<stop>', methods=['GET', 'POST'])
#@cross_origin
def alert_by_stop(stop):
    if stop.islower():
        return redirect(request.host_url + 'alert-by-stop/' + stop.upper(), code=301)

    try:
        data = mta.train_get_alert_by_stop(stop)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)

@app.route('/bus/alert-by-stop/<stop>', methods=['GET', 'POST'])
def bus_alert_by_stop(stop):
    if stop.islower():
        return redirect(request.host_url + 'bus/alert-by-stop/' + stop.upper(), code=301)

    try:
        data = mta.bus_get_alert_by_stop(stop)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)

@app.route('/alerts-by-route/<route>', methods=['GET', 'POST'])
def alerts_by_route(route):
    if route.islower():
        return redirect(request.host_url + 'alerts-by-route/' + route.upper(), code=301)

    data = mta.train_get_alerts_route(route)

    return jsonify({
        "data": data,
        "last_updated": mta.last_update()
    })

@app.route('/bus/alerts-by-route/<route>', methods=['GET', 'POST'])
def bus_alerts_by_route(route):
    if route.islower():
        return redirect(request.host_url + 'bus/alerts-by-route/' + route.upper(), code=301)

    data = mta.bus_get_alerts_route(route)

    return jsonify({
        "data": data,
        "last_updated": mta.last_update()
    })

@app.route('/all-alerts-by-route/<route>', methods=['GET', 'POST'])
def all_alerts_by_route(route):
    if route.islower():
        return redirect(request.host_url + 'all-alerts-by-route/' + route.upper(), code=301)

    try:
        data = mta.train_get_all_route_alerts(route)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)

@app.route('/bus/all-alerts-by-route/<route>', methods=['GET', 'POST'])
def bus_all_alerts_by_route(route):
    if route.islower():
        return redirect(request.host_url + 'bus/all-alerts-by-route/' + route.upper(), code=301)

    try:
        data = mta.bus_get_all_route_alerts(route)
        return _make_envelope(data)
    except KeyError as e:
        abort(404)

def _envelope_reduce(a, b):
    if a['last_update'] and b['last_update']:
        return a if a['last_update'] < b['last_update'] else b
    elif a['last_update']:
        return a
    else:
        return b

def _make_envelope(data):
    time = None
    if data:
        time = reduce(_envelope_reduce, data)['last_update']

    return jsonify({
        'data': data,
        'updated': time
        })

if __name__ == '__main__':
    app.run(use_reloader=False)

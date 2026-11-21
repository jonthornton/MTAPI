# coding: utf-8
"""
    mta-api-sanity
    ~~~~~~

    Expose the MTA's real-time subway feed as a json api

    :copyright: (c) 2014 by Jon Thornton.
    :license: BSD, see LICENSE for more details.
"""

from mtapi.mtapi import Mtapi, TrainFilter
from flask import Flask, request, Response, render_template, abort, redirect
import json
from datetime import datetime
from functools import wraps, reduce
import logging
import os

app = Flask(__name__)
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

class CustomJSONEncoder(json.JSONEncoder):
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

mta = Mtapi(
    app.config['STATIONS_FILE'],
    max_trains=app.config['MAX_TRAINS'],
    max_minutes=app.config['MAX_MINUTES'],
    expires_seconds=app.config['CACHE_SECONDS'],
    threaded=app.config['THREADED'])

def response_wrapper(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = f(*args, **kwargs)

        if not isinstance(resp, Response):
            # custom JSON encoder; this is important
            resp = Response(
                response=json.dumps(resp, cls=CustomJSONEncoder),
                status=200,
                mimetype="application/json"
            )

        add_cors_header(resp)

        return resp

    return decorated_function

def add_cors_header(resp):
    if app.config['DEBUG']:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    elif 'CROSS_ORIGIN' in app.config:
        resp.headers['Access-Control-Allow-Origin'] = app.config['CROSS_ORIGIN']

    return resp

def _error_response(message, status):
    resp = Response(
        response=json.dumps({'error': message}),
        status=status,
        mimetype="application/json"
    )

    return add_cors_header(resp)

@app.route('/')
@response_wrapper
def index():
    return {
        'title': 'MTAPI',
        'readme': 'Visit https://github.com/jonthornton/MTAPI for more info'
        }

@app.route('/by-location', methods=['GET'])
@response_wrapper
def by_location():
    try:
        location = (float(request.args['lat']), float(request.args['lon']))
    except KeyError as e:
        print(e)
        resp = Response(
            response=json.dumps({'error': 'Missing lat/lon parameter'}),
            status=400,
            mimetype="application/json"
        )

        return add_cors_header(resp)

    try:
        train_filter = _parse_train_filter(request.args)
    except ValueError as e:
        return _error_response(str(e), 400)

    data = mta.get_by_point(location, 5, train_filter)
    return _make_envelope(data)

@app.route('/by-route/<route>', methods=['GET'])
@response_wrapper
def by_route(route):

    if route.islower():
        url = request.host_url + 'by-route/' + route.upper()
        if request.query_string:
            url += '?' + request.query_string.decode()
        return redirect(url, code=301)

    try:
        train_filter = _parse_train_filter(request.args)
    except ValueError as e:
        return _error_response(str(e), 400)

    try:
        data = mta.get_by_route(route, train_filter)
        return _make_envelope(data)
    except KeyError as e:
        resp = Response(
            response=json.dumps({'error': 'Station not found'}),
            status=404,
            mimetype="application/json"
        )

        return add_cors_header(resp)

@app.route('/by-id/<id_string>', methods=['GET'])
@response_wrapper
def by_index(id_string):
    ids = id_string.split(',')

    try:
        train_filter = _parse_train_filter(request.args)
    except ValueError as e:
        return _error_response(str(e), 400)

    try:
        data = mta.get_by_id(ids, train_filter)
        return _make_envelope(data)
    except KeyError as e:
        resp = Response(
            response=json.dumps({'error': 'Station not found'}),
            status=404,
            mimetype="application/json"
        )

        return add_cors_header(resp)

@app.route('/stations', methods=['GET'])
@response_wrapper
def stations():
    return {
        'data': mta.get_stations(),
        'updated': mta.last_update()
        }

@app.route('/routes', methods=['GET'])
@response_wrapper
def routes():
    return {
        'data': sorted(mta.get_routes()),
        'updated': mta.last_update()
        }

def _parse_train_filter(args):
    route_ids = {r.strip().upper() for r in args.get('routes', '').split(',') if r.strip()} or None

    direction = args.get('dir', '').strip().upper() or None
    if direction is not None and direction not in ('N', 'S'):
        raise ValueError('Invalid dir parameter')

    max_trains = args.get('max_trains', '').strip() or None
    if max_trains is not None:
        max_trains = int(max_trains) if max_trains.isdecimal() else 0
        if max_trains < 1:
            raise ValueError('Invalid max_trains parameter')

    return TrainFilter(route_ids=route_ids, direction=direction, max_trains=max_trains)

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

    return {
        'data': data,
        'updated': time
    }

if __name__ == '__main__':
    app.run(use_reloader=False)

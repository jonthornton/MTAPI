# coding: utf-8
"""
    mta-api-sanity
    ~~~~~~

    Expose the MTA's real-time subway feed as a json api

    :copyright: (c) 2014 by Jon Thornton.
    :license: BSD, see LICENSE for more details.
"""

from mtapi.mtapi import Mtapi
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
    app.config['MTA_KEY'],
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

    data = mta.get_by_point(location, 5)
    return _make_envelope(data)

@app.route('/by-route/<route>', methods=['GET'])
@response_wrapper
def by_route(route):

    if route.islower():
        return redirect(request.host_url + 'by-route/' + route.upper(), code=301)

    try:
        data = mta.get_by_route(route)
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
        data = mta.get_by_id(ids)
        return _make_envelope(data)
    except KeyError as e:
        resp = Response(
            response=json.dumps({'error': 'Station not found'}),
            status=404,
            mimetype="application/json"
        )

        return add_cors_header(resp)

@app.route('/routes', methods=['GET'])
@response_wrapper
def routes():
    return {
        'data': sorted(mta.get_routes()),
        'updated': mta.last_update()
        }

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

# coding: utf-8
"""
    mta-api-sanity
    ~~~~~~

    Expose the MTA's real-time subway feed as a json api

    :copyright: (c) 2014 by Jon Thornton.
    :license: BSD, see LICENSE for more details.
"""

from mtapi import Mtapi
from flask import Flask, request, jsonify, render_template, abort
from flask.json import JSONEncoder
from datetime import datetime
from functools import wraps
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
    max_trains=app.config['MAX_TRAINS'],
    max_minutes=app.config['MAX_MINUTES'],
    expires_seconds=app.config['CACHE_SECONDS'],
    threaded=app.config['THREADED'])

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

@app.route('/')
@cross_origin
def index():
    return jsonify({
        'title': 'MTAPI',
        'readme': 'Visit https://github.com/jonthornton/MTAPI for more info'
        })

@app.route('/by-location', methods=['GET'])
@cross_origin
def by_location():
    try:
        location = (float(request.args['lat']), float(request.args['lon']))
    except KeyError as e:
        print e
        response = jsonify({
            'error': 'Missing lat/lon parameter'
            })
        response.status_code = 400
        return response

    return jsonify({
        'data': mta.get_by_point(location, 5),
        'updated': mta.last_update()
        })

@app.route('/by-route/<route>', methods=['GET'])
@cross_origin
def by_route(route):
    try:
        return jsonify({
            'data': mta.get_by_route(route),
            'updated': mta.last_update()
            })
    except KeyError as e:
        abort(404)

@app.route('/by-id/<id_string>', methods=['GET'])
@cross_origin
def by_index(id_string):
    ids = [ int(i) for i in id_string.split(',') ]
    try:
        return jsonify({
            'data': mta.get_by_id(ids),
            'updated': mta.last_update()
            })
    except KeyError as e:
        abort(404)

@app.route('/routes', methods=['GET'])
@cross_origin
def routes():
    return jsonify({
        'data': sorted(mta.get_routes()),
        'updated': mta.last_update()
        })

if __name__ == '__main__':
    app.run(use_reloader=False)

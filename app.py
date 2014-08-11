# coding: utf-8
"""
    mta-api-sanity
    ~~~~~~

    Expose the MTA's real-time subway feed as a json api

    :copyright: (c) 2014 by Jon Thornton.
    :license: BSD, see LICENSE for more details.
"""

import mta_realtime
from flask import Flask, request, jsonify, render_template, abort
from flask.json import JSONEncoder
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config.update(
    MAX_TRAINS=10,
    MAX_MINUTES=30,
    CACHE_SECONDS=60,
    THREADED=True
)
app.config.from_envvar('MTA_SETTINGS')

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

mta = mta_realtime.MtaSanitizer(
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
        'title': 'mta-api-sanity',
        'readme': 'Visit TODO for more info'
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
        'updated': mta.last_update(),
        'data': mta.get_by_point(location, 5)
        })

@app.route('/by-route/<route>', methods=['GET'])
@cross_origin
def by_route(route):
    try:
        return jsonify({
            'updated': mta.last_update(),
            'data': mta.get_by_route(route)
            })
    except KeyError as e:
        abort(404)

@app.route('/routes', methods=['GET'])
@cross_origin
def routes():
    return jsonify({
        'updated': mta.last_update(),
        'data': mta.get_routes()
        })

if __name__ == '__main__':
    app.run(use_reloader=False)

# coding: utf-8
"""
    mta-api-sanity
    ~~~~~~

    Expose the MTA's real-time subway feed as a json api

    :copyright: (c) 2014 by Jon Thornton.
    :license: BSD, see LICENSE for more details.
"""

import mta_realtime
from flask import Flask, request, jsonify, render_template
from flask_cors import cross_origin
from flask.json import JSONEncoder
from datetime import datetime
import time

app = Flask(__name__)
app.config.update(
    MAX_TRAINS=10,
    MAX_MINUTES=30,
    CACHE_SECONDS=10,
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
    app.config['STOPS_FILE'],
    max_trains=app.config['MAX_TRAINS'],
    max_minutes=app.config['MAX_MINUTES'],
    expires_seconds=app.config['CACHE_SECONDS'],
    threaded=app.config['THREADED'])

# def thread_loop(seconds):
#     global mta, app
#     time.sleep(seconds)
#     mta.update()
#     print mta.last_update()
#     threading.Thread(target=thread_loop, args=(app.config['CACHE_SECONDS'], )).start()

# if app.config['THREADED']:
#     threading.Thread(target=thread_loop, args=(app.config['CACHE_SECONDS'], ), daemon=True).start()

@app.route('/')
@cross_origin(headers=['Content-Type'])
def index():
    return jsonify({
        'title': 'mta-api-sanity',
        'readme': 'Visit TODO for more info'
        })

@app.route('/by-location', methods=['GET'])
@cross_origin(headers=['Content-Type'])
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
@cross_origin(headers=['Content-Type'])
def by_route(route):
    return jsonify({
        'updated': mta.last_update(),
        'data': mta.get_by_route(route)
        })

@app.route('/routes', methods=['GET'])
@cross_origin(headers=['Content-Type'])
def routes():
    return jsonify({
        'updated': mta.last_update(),
        'data': mta.get_routes()
        })

if __name__ == '__main__':
    app.run()

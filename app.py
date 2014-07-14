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
from flask.json import JSONEncoder
from datetime import datetime

app = Flask(__name__)
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

mta = mta_realtime.MtaSanitizer(app.config['MTA_KEY'], app.config['STOPS_FILE'])

@app.route('/')
def index():
    return jsonify({
        'title': 'mta-api-sanity',
        'readme': 'Visit TODO for more info'
        })

@app.route('/by-location', methods=['GET'])
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
        'updated': mta.lastUpdate(),
        'data': mta.getByPoint(location, 5)
        })

if __name__ == '__main__':
    app.run()

from mtapi import Mtapi

def test_init():
    from app import app
    mta = Mtapi(
        app.config['MTA_KEY'],
        app.config['STATIONS_FILE'],
        max_trains=app.config['MAX_TRAINS'],
        max_minutes=app.config['MAX_MINUTES'],
        expires_seconds=app.config['CACHE_SECONDS'],
        threaded=app.config['THREADED'])

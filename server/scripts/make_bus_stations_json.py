# Given stations.csv, creates a stations.json of stop groupings where each group's lat/lon is the average of its member stops.

import argparse, csv, json, sys
from hashlib import md5

ID_LENGTH = 8

def main():
    parser = argparse.ArgumentParser(description='Generate stations JSON file for MtaSanitize server.')
    parser.add_argument('stations_file', default='stations.json')
    args = parser.parse_args()

    stations = {}
    with open(args.stations_file, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:

            if row['parent_id'] in stations:
                stations[row['parent_id']]['stops'][row['stop_id']] = [float(row['lat']), float(row['lon'])]
                stations[row['parent_id']]['name'].add(row['name'])
            else:
                stations[row['parent_id']] = {
                    'name': set([row['name']]),
                    'stops': {
                        row['stop_id']: [float(row['lat']), float(row['lon'])]
                    }
                }

    keyed_stations = {}
    for station in stations.values():
        station['name'] = ' / '.join(station['name'])
        station['location'] = [
            sum(v[0] for v in station['stops'].values()) / float(len(station['stops'])),
            sum(v[1] for v in station['stops'].values()) / float(len(station['stops']))
        ]
        station['id'] = ''.join(station['stops'].keys())[:ID_LENGTH]

        keyed_stations[station['id']] = station

    json.dump(keyed_stations, sys.stdout, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()

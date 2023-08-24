# Given stations.csv, creates a stations.json of stop groupings where each group's lat/lon is the average of its member stops.

import argparse, csv, json, sys
from hashlib import md5

ID_LENGTH = 4

def main():
    parser = argparse.ArgumentParser(description='Generate stations JSON file for MtaSanitize server.')
    parser.add_argument('stations_file', default='stations.json')
    args = parser.parse_args()

    # group stations by parent_id
    stations = {}
    with open(args.stations_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:

            if row['parent_id'] in stations:
                stations[row['parent_id']]['stops'][row['stop_id']] = [float(row['lat']), float(row['lon'])]
                stations[row['parent_id']]['name'].add(row['name'])
            else:
                stations[row['parent_id']] = {
                    'id': row['parent_id'],
                    'name': set([row['name']]),
                    'stops': {
                        row['stop_id']: [float(row['lat']), float(row['lon'])]
                    }
                }

    # concatenate names and average lat/lng's
    for id, station in stations.items():
        station['name'] = ' / '.join(station['name'])
        station['location'] = [
            sum(v[0] for v in station['stops'].values()) / float(len(station['stops'])),
            sum(v[1] for v in station['stops'].values()) / float(len(station['stops']))
        ]
        stations[id] = station

    json.dump(stations, sys.stdout, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()

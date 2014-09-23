# Given stations.csv, creates a stations.json of stop groupings where each group's lat/lon is the average of its member stops.

import argparse, csv, json, sys

def main():
    parser = argparse.ArgumentParser(description='Generate stations JSON file for MtaSanitize server.')
    parser.add_argument('stations_file', default='stations.json')
    args = parser.parse_args()

    stations = {}
    with open(args.stations_file, 'rb') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                stations[row['parent_id']]['stops'][row['stop_id']] = [float(row['lat']), float(row['lon'])]
                stations[row['parent_id']]['name'].add(row['name'])
            except KeyError as e:
                stations[row['parent_id']] = {
                    'name': set([row['name']]),
                    'stops': {
                        row['stop_id']: [float(row['lat']), float(row['lon'])]
                    }
                }

    for station in stations.values():
        station['name'] = ' / '.join(station['name'])
        station['lat'] = sum(v[0] for v in station['stops'].values()) / float(len(station['stops']))
        station['lon'] = sum(v[1] for v in station['stops'].values()) / float(len(station['stops']))

    json.dump(stations.values(), sys.stdout, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()

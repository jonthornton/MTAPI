# Given GTFS stops.txt and transfers.txt, creates a stations.csv file of station groupings based on stations connected in transfers.txt.
# The stations.csv file can be edited to relabel and reorganize the groupings (groupings of more than one station appear at the top of the file).
# The edited stations.csv can be converted to a stations.json by make_stations_json.py.
# Assumes that transfers.txt only refers to GTFS "stations" (location_type 1) and that transfers.txt has transitive closure.

import argparse, csv, json, sys

def main():
    parser = argparse.ArgumentParser(description='Generate stations CSV file for use with make_stations_json.py')
    parser.add_argument('stops_file', default='stops.txt')
    parser.add_argument('transfers_file', default='transfers.txt')
    args = parser.parse_args()

    stops = {}
    transfers = {}

    # load stops into a dict
    with open(args.stops_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['parent_station']:
                continue

            stops[row['stop_id']] = {
                'name': row['stop_name'],
                'lat': row['stop_lat'],
                'lon': row['stop_lon']
                }

    # load transfer groups into a dict. duplicates will be filtered out later
    with open(args.transfers_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['from_stop_id'] == row['to_stop_id']:
                continue

            try:
                transfers[row['from_stop_id']].add(row['to_stop_id'])
            except KeyError as e:
                transfers[row['from_stop_id']] = set([row['from_stop_id'], row['to_stop_id']])

    # write CSV to stdout
    writer = csv.writer(sys.stdout)
    writer.writerow(['stop_id', 'name', 'lat', 'lon', 'parent_id'])

    # write grouped stops first for easy editing
    for parent_id in transfers:
        # skip duplicate groups
        if parent_id > min(transfers[parent_id]):
            continue

        for stop_id in transfers[parent_id]:
            stop = stops.pop(stop_id)
            writer.writerow([stop_id, stop['name'], stop['lat'], stop['lon'], parent_id])

    # write the non-grouped stops
    for stop_id in stops:
        writer.writerow([stop_id, stops[stop_id]['name'], stops[stop_id]['lat'], stops[stop_id]['lon'], stop_id])


if __name__ == '__main__':
    main()

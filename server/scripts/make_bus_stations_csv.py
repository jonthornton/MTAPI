import argparse, csv, json, sys, os


def main():
    parser = argparse.ArgumentParser(description='Generate bus stations CSV file for use with make_bus_stations_json.py')
    parser.add_argument('stops_file_dir', default='stops')
    args = parser.parse_args()

    stops = {}

    # keep track of the first time a stop is seen (multiple routes stop at the same station case)
    parents = {}

    for filename in os.listdir(args.stops_file_dir):
        # load stops into a dict
        with open(os.path.join(args.stops_file_dir, filename), 'rt') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['parent_station']:
                    continue

                if row['stop_name'] in parents.keys():
                    stops[row['stop_id']] = {
                        'name': row['stop_name'],
                        'lat': row['stop_lat'],
                        'lon': row['stop_lon'],
                        'parent_id': parents[row['stop_name']]
                    }
                else:
                    parents[row['stop_name']] = row['stop_id']
                    stops[row['stop_id']] = {
                        'name': row['stop_name'],
                        'lat': row['stop_lat'],
                        'lon': row['stop_lon'],
                        'parent_id': row['stop_id']
                    }

    # write CSV to stdout
    writer = csv.writer(sys.stdout)
    writer.writerow(['stop_id', 'name', 'lat', 'lon', 'parent_id'])

    # write the non-grouped stops
    for stop_id in stops:
        writer.writerow([stop_id, stops[stop_id]['name'], stops[stop_id]['lat'], stops[stop_id]['lon'], stops[stop_id]['parent_id']])


if __name__ == '__main__':
    main()

# Given stations.csv, creates a stations.json of stop groupings where each group's lat/lon is the average of its member stops.

import csv
import json

# Load stations.csv.
stations_csv = {}
f_stations_csv = open('stations.csv', 'r')
reader = csv.reader(f_stations_csv, delimiter=',', quotechar='"')
reader.next()   # skip header
for line in reader:
	if line[0] not in stations_csv:
		stations_csv[line[0]] = [line[1], []]
		stations_csv[line[0]] = {}
		stations_csv[line[0]]['name'] = line[1]
		stations_csv[line[0]]['stops'] = {}
	stations_csv[line[0]]['stops'][line[2]] = [float(line[4]), float(line[5])]
f_stations_csv.close()

# Generate stations.json.
stations_json = []
for group in stations_csv:
	stop_lat_sum = 0
	stop_lon_sum = 0
	stop_count = 0
	stations_json += [stations_csv[group]]
	for stop in stations_csv[group]['stops']:
		stop_lat_sum += stations_csv[group]['stops'][stop][0]
		stop_lon_sum += stations_csv[group]['stops'][stop][1]
		stop_count += 1
	stations_json[-1]['location'] = [round(stop_lat_sum / stop_count, 6), round(stop_lon_sum / stop_count, 6)]
f_stations_json = open('stations.json', 'w')
f_stations_json.write(json.dumps(stations_json))
f_stations_json.close()


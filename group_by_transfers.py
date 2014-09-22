# Given GTFS stops.txt and transfers.txt, creates a stations.csv file of station groupings based on stations connected in transfers.txt.
# The stations.csv file can be edited to relabel and reorganize the groupings (groupings of more than one station appear at the top of the file).
# The edited stations.csv can be converted to a stations.json by generate_stations_json.py.
# Assumes that transfers.txt only refers to GTFS "stations" (location_type 1) and that transfers.txt has transitive closure.

import csv

# Load GTFS "stations" from stops.txt.
stops = {}
transfers = {}
f_stops = open('stops.txt', 'r')
reader = csv.reader(f_stops, delimiter=',', quotechar='"')
reader.next()	# skip header
for line in reader:
	stops[line[0]] = [line[1], line[2], line[3], line[4], line[5]]
	if line[4] == '1':	# GTFS station
		transfers[line[0]] = [line[0]]
f_stops.close()

# Load transfers from GTFS transfers.txt.
f_transfers = open('transfers.txt', 'r')
reader = csv.reader(f_transfers, delimiter=',', quotechar='"')
reader.next()	# skip header
for line in reader:
	if line[1] != line[0]:
		transfers[line[0]] += [line[1]]
f_transfers.close()

# Write connected stations as groups.
f_stations = open('stations.csv', 'w')
writer = csv.writer(f_stations, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerow(['group_id', 'group_name', 'stop_id', 'stop_name', 'stop_lat', 'stop_lon'])
# Write groups of more than one first so that they appear at the top of the stations CSV for easier editing.
for from_stop_id in transfers:
	if min(transfers[from_stop_id]) < from_stop_id or len(transfers[from_stop_id]) < 2:
		continue
	for to_stop_id in transfers[from_stop_id]:
		writer.writerow(['G' + from_stop_id, stops[from_stop_id][0], to_stop_id, stops[to_stop_id][0], stops[to_stop_id][1], stops[to_stop_id][2]])
# Write groups of one.
for from_stop_id in transfers:
        if min(transfers[from_stop_id]) < from_stop_id or len(transfers[from_stop_id]) > 1:
                continue
        for to_stop_id in transfers[from_stop_id]:
                writer.writerow(['G' + from_stop_id, stops[from_stop_id][0], to_stop_id, stops[to_stop_id][0], stops[to_stop_id][1], stops[to_stop_id][2]])
f_stations.close()


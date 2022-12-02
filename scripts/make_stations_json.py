import requests
import csv
import json
import sys
import argparse


# This URL comes from the MTA developer data
# http://web.mta.info/developers/developer-data-terms.html#data
DEFAULT_STATIONS_URL = "https://atisdata.s3.amazonaws.com/Station/Stations.csv"


def main():
    parser = argparse.ArgumentParser(
        description="Generate stations JSON file for MtaSanitize server.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-o", "--output", default="stations.json", help="Where to output the file to, use - for stdout.")
    parser.add_argument("-u", "--url", default=DEFAULT_STATIONS_URL, help="Where to get the stations CSV from.")
    args = parser.parse_args()

    output = {}
    with requests.get(args.url) as r:

        reader = csv.DictReader(r.text.splitlines())
        for row in reader:
            if not row["Complex ID"] in output:
                output[row["Complex ID"]] = {
                    "id": row["Complex ID"],
                    "location": [row["GTFS Latitude"], row["GTFS Longitude"]],
                    "name": row["Stop Name"],
                    "stops": {},
                }
            output[row["Complex ID"]]["stops"][row["GTFS Stop ID"]] = [
                row["GTFS Latitude"],
                row["GTFS Longitude"],
            ]

    if args.output == "-":
        json.dump(output, sys.stdout, indent=True)
    else:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=True)

if __name__ == "__main__":
    main()

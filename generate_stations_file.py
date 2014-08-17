import argparse
import mta_realtime

def main():
    DEFAULT_THRESHOLD = 0.0025

    parser = argparse.ArgumentParser(description='Generate stations JSON file for MtaSanitize server.')
    parser.add_argument('stops_file', default='stops.txt')
    parser.add_argument('outfile', default='stations.json')
    parser.add_argument('--threshold',
                        help='Grouping threshold; defaults to '+str(DEFAULT_THRESHOLD),
                        type=int,
                        default=DEFAULT_THRESHOLD)

    args = parser.parse_args()

    mta_realtime.generate_stations_file(args.stops_file, args.outfile, args.threshold)
    print 'Generated '+args.outfile

if __name__ == '__main__':
    main()

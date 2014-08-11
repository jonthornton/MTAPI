import sys, mta_realtime

def main():
    if len(sys.argv) != 3:
        print 'Usage: python generate_stations_file.py [stops_file] [output_path]'
        exit()

    mta_realtime.generate_stations_file(sys.argv[1], sys.argv[2])
    print 'Generated '+sys.argv[2]

if __name__ == '__main__':
    main()

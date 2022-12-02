#! /usr/bin/nix-shell
#! nix-shell -p protobuf curl

set -euo pipefail

curl https://api.mta.info/nyct-subway.proto.txt -o nyct-subway.proto
curl https://developers.google.com/static/transit/gtfs-realtime/gtfs-realtime.proto -o gtfs-realtime.proto

protoc -I=. --python_out=. nyct-subway.proto gtfs-realtime.proto


# Fix nyct-subway pythom import to be relative path
sed -i \
  -e 's/import gtfs_realtime_pb2 as gtfs__realtime__pb2/from . import gtfs_realtime_pb2 as gtfs__realtime__pb2/' \
  nyct_subway_pb2.py

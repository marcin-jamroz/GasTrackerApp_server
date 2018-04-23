#!/usr/bin/python

import sys
import json

srcfile = sys.argv[1]
outfile = sys.argv[2]

print(str.format('Converting file: {}', str(srcfile)))


table_name = "gas_stations"

create_table = str.format("CREATE TABLE IF NOT EXISTS {} (\
  PRIMARY KEY (station_id),\
  network_name VARCHAR(256),\
  network_id INTEGER,\
  point GEOMETRY NOT NULL\
)", table_name)

insert_into = "INSERT INTO gas_stations(station_id, network_name, network_id,\
point) VALUES\n"

value = "\t({}, '{}', {}, ST_PointFromText('POINT({} {})')"


stations = json.load(open(srcfile))

with open(outfile, 'w') as f:
    f.write(create_table)
    f.write("\n")
    f.write(insert_into)

    for i in range(len(stations)):
      station = stations[i]
      f.write(str.format(value,\
          station["station_id"],\
          station["network_name"],\
          station["network_id"],\
          station["x"],\
          station["y"]))
      if (i == len(stations) - 1):
          f.write(";\n")
      else:
          f.write(",\n")






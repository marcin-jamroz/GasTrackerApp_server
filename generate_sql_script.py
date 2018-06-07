#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import random

srcfile = sys.argv[1]
outfile = sys.argv[2]

print(str.format('Converting file: {}', str(srcfile)))

table_name = "gas_stations"

create_table = str.format("CREATE TABLE IF NOT EXISTS {} (\
  station_id INTEGER PRIMARY KEY,\
  network_name VARCHAR(256),\
  network_id INTEGER,\
  price JSONB DEFAULT '{{}}',\
  cluster_id INTEGER DEFAULT NULL,\
  updated TIMESTAMP DEFAULT NULL,\
  point GEOMETRY NOT NULL\
);\n", table_name)

insert_into = "INSERT INTO gas_stations(station_id, network_name, network_id, price, point) VALUES\n"

value = "\t({}, '{}', {}, '{}', ST_PointFromText('POINT({} {})'))"

stations = json.load(open(srcfile))

with open(outfile, 'w') as f:
    f.write(create_table)
    f.write("\n")
    f.write(insert_into)

    for i in range(len(stations)):
        station = stations[i]

        sjson = json.dumps(
            {"LPG": round(random.uniform(2.0, 2.2), 2),
             "PB95": round(random.uniform(5, 5.5), 2),
             "ON": round(random.uniform(4.5, 4.8),2)})

        f.write(str.format(value, \
                           station["station_id"], \
                           station["network_name"], \
                           station["network_id"], \
                           sjson, \
                           station["x"], \
                           station["y"]))

        if (i == len(stations) - 1):
            f.write(";\n")
        else:
            f.write(",\n")

#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import json
import random

srcfile = sys.argv[1]
outfile = sys.argv[2]

print(str.format('Converting file: {}', str(srcfile)))

table_name = "gas_networks"

create_table = str.format("CREATE TABLE IF NOT EXISTS {} (\
  network_id INTEGER PRIMARY KEY,\
  network_name VARCHAR(256)\
);\n", table_name)

insert_into = "INSERT INTO gas_networks(network_id, network_name) VALUES\n"

value = "\t({}, '{}')"

stations = json.load(open(srcfile))

network_ids = []

with open(outfile, 'w') as f:
    f.write(create_table)
    f.write("\n")
    f.write(insert_into)

    for i in range(len(stations)):
        station = stations[i]

        if (station["network_id"] in network_ids):
            continue

        f.write(str.format(value,\
                           station["network_id"], \
                           station["network_name"].encode('utf-8')))
        network_ids.append(station["network_id"])

        f.write(",\n")

    f.seek(-2, os.SEEK_END)
    f.truncate()
    f.write(";\n")

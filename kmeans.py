import sys
import numpy as np
from sklearn.cluster import KMeans
import json

outfile = sys.argv[1]
number = int(sys.argv[2])

stations = json.load(open("./gas_stations.json"))

stations_x = []
stations_y = []
stations_id = []

for s in stations:
    stations_x.append(s["x"])
    stations_y.append(s["y"])
    stations_id.append(s["station_id"])

### For the purposes of this example, we store feature data from our
### dataframe `df`, in the `f1` and `f2` arrays. We combine this into
### a feature matrix `X` before entering it into the algorithm.

f1 = stations_x
f2 = stations_y

k = number

X = np.array(list(zip(f1, f2)), dtype=np.float32)
kmeans = KMeans(n_clusters=k).fit(X)

C = kmeans.cluster_centers_
cluster_idxs = kmeans.predict(X)


# clusters table

table_name = "clusters"

create_table = str.format("CREATE TABLE IF NOT EXISTS {} (\
  cluster_id INTEGER PRIMARY KEY,\
  center GEOMETRY NOT NULL\
);\n", table_name)

insert_into = "INSERT INTO clusters(cluster_id, center) VALUES\n"

value = "\t({}, ST_PointFromText('POINT({} {})'))"

with open(outfile, 'w') as f:
    f.write(create_table)
    f.write("\n")
    f.write(insert_into)

    for i in range(len(kmeans.cluster_centers_)):
        f.write(str.format(value, i, kmeans.cluster_centers_[i][0], kmeans.cluster_centers_[i][1]))

        if i == len(kmeans.cluster_centers_) - 1:
            f.write(" ON CONFLICT (cluster_id) DO UPDATE SET center=EXCLUDED.center;\n")
        else:
            f.write(",\n")




# stations update


table_name = "gas_stations"

update_into = "UPDATE gas_stations as gas SET cluster_id = c.c_id from (VALUES {}) as c(c_id, s_id) WHERE gas.station_id = c.s_id;\n"

with open(outfile, 'a') as f:

    values = []
    for i in range(len(kmeans.labels_)):
        values.append((kmeans.labels_[i], stations_id[i]))

    str_values = str(values)

    f.write(str.format(update_into, str_values[1:-1]))

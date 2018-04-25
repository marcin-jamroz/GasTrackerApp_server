import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib
import json


stations = json.load(open("/home/raqu/Desktop/stations_db/gas_stations.json"))

stations_x = []
stations_y = []

for s in stations:
    stations_x.append(s["x"])
    stations_y.append(s["y"])

### For the purposes of this example, we store feature data from our
### dataframe `df`, in the `f1` and `f2` arrays. We combine this into
### a feature matrix `X` before entering it into the algorithm.

f1 = stations_x
f2 = stations_y

k = 100

X=np.array(list(zip(f1, f2)), dtype=np.float32)
kmeans = KMeans(n_clusters=k).fit(X)

C = kmeans.cluster_centers_
cluster_idxs = kmeans.predict(X)

colors = ['r', 'g', 'b', 'y', 'c', 'm']

plt.scatter(X[:, 0], X[:, 1], c=cluster_idxs)
plt.scatter(C[:, 0], C[:, 1], marker='*', s=200, c='#050505')

plt.axis('scaled')
plt.show()


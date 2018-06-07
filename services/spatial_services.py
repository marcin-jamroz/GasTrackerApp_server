from sqlalchemy.sql import text

# query_cheapest_station_test = text(
#     '''SELECT station_id, price, cluster_id, extract(epoch from updated) as updated,
#               network_id, ST_X(point) as lat, ST_Y(point) as lng, ST_DISTANCE(Geography(ST_POINT(50.5380, 22.7228)), Geography(gs.point)) as dist
#         FROM gas_stations gs
#         WHERE gs.cluster_id IN ( SELECT cluster_id FROM clusters c WHERE cluster_id=c.cluster_id
#                       ORDER BY ST_DISTANCE(ST_POINT(50.5380, 22.7228), c.center) LIMIT 5)
#         ORDER BY gs.price->>'LPG', dist
#         LIMIT 3;''')


def getClusterStations(db, latitude, longitude, fuel, cheapN, closeN):

    # Get stations from 5 nearest clusters to user and sort them by price and then by distance
    query_cheapest_station = text(
        '''SELECT station_id, price, cluster_id, extract(epoch from updated) as updated,
                  network_id, ST_X(point) as lat, ST_Y(point) as lng
            FROM gas_stations gs
            WHERE gs.cluster_id IN ( SELECT cluster_id FROM clusters c WHERE cluster_id=c.cluster_id
                          ORDER BY ST_DISTANCE(ST_POINT(:lat, :lng), c.center) LIMIT 3)
            ORDER BY gs.price->>:fuel, ST_DISTANCE(ST_POINT(:lat, :lng), gs.point)
            LIMIT :n;''')

    cheapest_stations = db.engine.execute(query_cheapest_station, {'lat': latitude, 'lng': longitude, 'fuel': fuel, 'n': cheapN}).fetchall()

    # Get stations from 5 nearest clusters to user and sort them by distance
    query_closest_station = text(
        '''SELECT station_id, price, cluster_id, extract(epoch from updated) as updated,
                  network_id, ST_X(point) as lat, ST_Y(point) as lng
            FROM gas_stations gs
            WHERE gs.cluster_id IN ( SELECT cluster_id FROM clusters c WHERE cluster_id=c.cluster_id
                          ORDER BY ST_DISTANCE(ST_POINT(:lat, :lng), c.center) LIMIT 3)
            ORDER BY ST_DISTANCE(ST_POINT(:lat, :lng), gs.point)
            LIMIT :n;''')

    closest_stations = db.engine.execute(query_closest_station, {'lat': latitude, 'lng': longitude, 'n': closeN}).fetchall()

    cheapest_stations = [dict(x) for x in cheapest_stations]
    closest_stations = [dict(x) for x in closest_stations]
    result = {'cheapest_stations': cheapest_stations, 'closest_stations': closest_stations}
    return result


def getStationsFromRadius(db, point, radius):
    if (not (radius or point or db)):
        return []

    query = ''' SELECT station_id, price, cluster_id, extract(epoch from updated) as updated,
                       network_id, ST_X(point) as lat, ST_Y(point) as lng
                FROM gas_stations
                WHERE ST_Distance_Sphere(point, ST_MakePoint(:lat,:lng)) <= :radius'''

    result = db.engine.execute(text(query), {
        "lat": point["lat"],
        "lng": point["lng"],
        "radius": radius
    })
    if (result):
        return [dict(r) for r in result]
    else:
        return []


def getClusterWithBounds(db, id, boundtype="Polygon"):
    bound_query = ""
    if (boundtype == "Polygon"):
        bound_query = "ST_ConvexHull(ST_Collect(g.point))"
    elif (boundtype == "Circle"):
        bound_query = "ST_MinimumBoundingCircle(ST_Collect(g.point))"
    else:
        raise Exception("Unsupported bounding geometry type {0}".format(boundtype))

    result = None
    if (id):
        query = ''' SELECT  c.cluster_id,
            ST_X(c.center) AS lat,
            ST_Y(c.center) AS lng,
            ST_AsGeoJSON({0})::json as bounding
        FROM gas_stations AS g, clusters AS c WHERE g.cluster_id = :id AND g.cluster_id = c.cluster_id
        GROUP BY c.cluster_id;'''.format(bound_query)

        result = db.engine.execute(text(query), {
            "id": id
        }).fetchone()
        if (result):
            return dict(result)
        return None

    else:
        query = ''' SELECT  c.cluster_id,
                    ST_X(center) AS lat,
                    ST_Y(center) AS lng,
                    ST_AsGeoJSON({0})::json as bounding
                FROM gas_stations AS g, clusters AS c WHERE g.cluster_id = c.cluster_id
                GROUP BY c.cluster_id;'''.format(bound_query)

        result = db.engine.execute(text(query))
        if (result):
            return [dict(r) for r in result]
        else:
            return []


def getRouteStations(db, route, maxdist):
    mDist = 500.0 # default maxdist value
    if (maxdist):
        mDist = maxdist

    route_str = ""
    for i in range(len(route) - 1):
        rpoint = route[i]
        route_str += "{0} {1}, ".format(rpoint[0], rpoint[1])
    route_str += "{0} {1}".format(route[len(route) - 1][0], route[len(route) - 1][1])

    query = ''' SELECT station_id, price, cluster_id, extract(epoch from updated) as updated, network_id, ST_X(point) as lat, ST_Y(point) as lng
                FROM gas_stations
                WHERE ST_DWithin(Geography(ST_GeomFromText({0})), Geography(point), :mdist);'''.format("'LINESTRING({0})'".format(route_str))

    result = db.engine.execute(text(query), {
        'mdist': mDist
    }).fetchall()

    if (result):
        return [dict(r) for r in result]
    return []

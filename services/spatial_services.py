from sqlalchemy.sql import text


def getClusterStations(db, latitude, longitude, fuel):
    query_cluster = text('''SELECT c.cluster_id, c.center FROM clusters c ORDER BY ST_DISTANCE(ST_POINT(:lat, :lng), c.center) LIMIT 1;
''')
    cluster = db.engine.execute(query_cluster, {'lat': latitude, 'lng': longitude}).fetchone()
    print(cluster)

    query_cheapest_station = text(
        '''SELECT station_id, price, cluster_id, extract(epoch from updated) as updated, network_id, ST_X(point) as lat, ST_Y(point) as lng FROM gas_stations gs WHERE gs.cluster_id = :cluster_id AND gs.price->>:fuel= (SELECT MIN(g.price->>:fuel) FROM gas_stations g WHERE cluster_id=:cluster_id);''')
    cheapest_stations = db.engine.execute(query_cheapest_station,
                                          {'cluster_id': cluster['cluster_id'], 'fuel': fuel}).fetchall()

    query_closest_station = text(
        '''SELECT station_id, price, cluster_id, extract(epoch from updated) as updated, network_id, ST_X(point) as lat, ST_Y(point) as lng FROM gas_stations g WHERE g.cluster_id = :cluster_id ORDER BY ST_DISTANCE(ST_POINT(:lat, :lng), :cluster_point) LIMIT 1;''')
    closest_station = db.engine.execute(query_closest_station,
                                        {'cluster_id': cluster['cluster_id'], 'lat': latitude, 'lng': longitude,
                                         'cluster_point': cluster['center']}).fetchone()

    cheapest_stations = [dict(x) for x in cheapest_stations]
    result = {'cheapest_stations': cheapest_stations, 'closest_station': dict(closest_station)}
    return result


def getStationsFromRadius(db, point, radius):
    if (not (radius or point or db)):
        return []

    query = '''SELECT station_id, price, cluster_id, extract(epoch from updated) as updated, network_id, ST_X(point) as lat, ST_Y(point) as lng FROM gas_stations WHERE
                          ST_Distance_Sphere(point, ST_MakePoint(:lat,:lng)) <= :radius'''
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

    query = ''' SELECT station_id, price, cluster_id, extract(epoch from updated) as updated, network_id, ST_X(point) as lat, ST_Y(point) as lng
                FROM gas_stations
                WHERE ST_DWithin(ST_GeomFromText(:route), point, :mdist);'''

    route_str = ""
    for i in range(len(route) - 1):
        rpoint = route[i]
        route_str += "{0} {1}, ".format(rpoint[0], rpoint[1])
    route_str += "{0} {1}".format(route[len(route) - 1][0], route[len(route) - 1][1])

    result = db.engine.execute(query, {
        'route': "'LINESTRING({0})'".format(route_str),
        'mdist': mDist
    }).fetchall()

    return result
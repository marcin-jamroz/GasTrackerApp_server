from sqlalchemy.sql import text


def getStationsFromRadius(db, point, radius):
    if (not (radius or point or db)):
        return []

    query = '''SELECT *, ST_X(point) as lat, ST_Y(point) as lng FROM gas_stations WHERE
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


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


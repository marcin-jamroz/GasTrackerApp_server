from flask import Flask, jsonify, request
import os, traceback, time, datetime, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

from services.spatial_services import getStationsFromRadius, getClusterWithBounds, getClusterStations, getRouteStations

app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']
print()
print(DATABASE_URL)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)


@app.route('/')
def home():
    return jsonify({
        "version": "1.0.0",
        "authors": [ "Marcin Jamroz", "Filip Rak" ],
        "name": "gas-tracker-app"
    }), 200

@app.route('/cluster_stations')
def get_cluster_stations():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    fuel = request.args.get('fuel')

    result = getClusterStations(db, lat, lng, fuel)
    return jsonify(result)

@app.route('/route_stations', methods=["POST"])
def get_route_stations():
    try:
        maxdist = request.args.get('maxdist')
        data = request.get_json(force=True)
        if "route" not in data or not data["route"]:
            raise Exception("A valid 'route' parameter is required in request body (array of [lat, lng])")

        return jsonify(getRouteStations(db, data["route"]), maxdist)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "type":type(e).__name__,
            "message":e.message if hasattr(e, 'message') else str(e)
        }), 400

@app.route('/prices')
def prices():
    station_id = request.args.get('station_id')

    pb95 = request.args.get('PB95')
    on = request.args.get('ON')
    lpg = request.args.get('LPG')

    try:
        prices_dict = {}
        if (pb95):
            prices_dict['PB95'] = round(float(pb95), 2)
        if (on):
            prices_dict['ON'] = round(float(on), 2)
        if (lpg):
            prices_dict['LPG'] = round(float(lpg), 2)

        if (not station_id):
            raise Exception('Correct station id is required in url param')

        if (not (pb95 or lpg or on)):
            raise Exception('At least one of: LPG | PB95 | ON price is required in url param')

        query = '''UPDATE gas_stations
                    SET price = price || jsonb :pricejson,
                        updated = to_timestamp(:updatetime)
                    WHERE station_id=:id'''

        ts = time.time()

        result = db.engine.execute(text(query), {
            "id" : int(station_id),
            "pricejson": json.dumps(prices_dict),
            "updatetime": ts
        })
        if (result.rowcount == 1):
            prices_dict["status"] = "OK"
            prices_dict["station_id"] = int(station_id)
            prices_dict["updated"] = ts
            return jsonify(prices_dict), 200
        else:
            return jsonify({
                "type": "NotFound",
                "message": "Error updating price for station id {0}".format(station_id)
            }), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "type":type(e).__name__,
            "message":e.message if hasattr(e, 'message') else str(e)
        }), 400


@app.route('/stations', defaults={'id': None})
@app.route('/stations/<id>')
def get_station(id):
    radius = request.args.get('radius')
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    try:
        if (radius and lat and lng):
            return jsonify(getStationsFromRadius(db, { "lat":lat, "lng":lng }, radius))

        query = ''' SELECT station_id, price, cluster_id, extract(epoch from updated) as updated, network_id, ST_X(point) as lat, ST_Y(point) as lng
                    FROM gas_stations WHERE station_id=:id'''
        result = db.engine.execute(text(query), {"id" : id}).fetchone()
        if (result):
            return jsonify(dict(result)), 200
        else:
            return jsonify({
                "type": "NotFound",
                "message": "Data not found for id {0}".format(id)
            }), 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "type":type(e).__name__,
            "message":e.message if hasattr(e, 'message') else str(e)
        }), 400


@app.route('/networks', defaults={'id': None})
@app.route('/networks/<id>')
def get_network(id):
    try:
        if (id):
            query = '''SELECT * FROM gas_networks WHERE network_id=:id'''
            result = db.engine.execute(text(query), {"id" : id}).fetchone()
            if (result):
                return jsonify(dict(result)), 200
            else:
                return jsonify({
                    "type": "NotFound",
                    "message": "Data not found for id {0}".format(id)
                }), 404
        else:
            query = '''SELECT * FROM gas_networks'''
            result = db.engine.execute(text(query))
            return jsonify([dict(r) for r in result]), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "type":type(e).__name__,
            "message":e.message if hasattr(e, 'message') else str(e)
        }), 400


@app.route('/clusters', defaults={'id': None})
@app.route('/clusters/<id>')
def clusters(id):
    bounding = request.args.get('bounding')
    try:
        if (id):
            result = None
            jsonified = None
            if (bounding):
                result = getClusterWithBounds(db, id, bounding)
                jsonified = jsonify(result)
            else:
                query = '''SELECT *, ST_X(center) as lat, ST_Y(center) as lng FROM clusters WHERE cluster_id=:id'''
                result = db.engine.execute(text(query), {"id" : id}).fetchone()
                jsonified = jsonify(dict(result))

            if (not result):
                return jsonify({
                    "type": "NotFound",
                    "message": "Data not found for id {0}".format(id)
                }), 404
            return jsonified, 200
        else:
            if (bounding):
                return jsonify(getClusterWithBounds(db, None, bounding))

            query = '''SELECT *, ST_X(center) as lat, ST_Y(center) as lng FROM clusters'''
            result = db.engine.execute(text(query))
            return jsonify([dict(r) for r in result]), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "type":type(e).__name__,
            "message":e.message if hasattr(e, 'message') else str(e)
        }), 400



if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, request
import os, traceback
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

from services.spatial_services import getStationsFromRadius


app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']
print()
print(DATABASE_URL)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)


@app.route('/')
def home():
    return jsonify({
        "version": "0.0.1",
        "authors": [ "Marcin Jamroz", "Filip Rak" ],
        "name": "gas-tracker-app"
    }), 200

@app.route('/stations', defaults={'id': None})
@app.route('/stations/<id>')
def get_station(id):
    radius = request.args.get('radius')
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    try:
        if (radius and lat and lng):
            return jsonify(getStationsFromRadius(db, { "lat":lat, "lng":lng }, radius))

        query = '''SELECT *, ST_X(point) as lat, ST_Y(point) as lng  FROM gas_stations WHERE station_id=:id'''
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
    try:
        if (id):
            query = '''SELECT *, ST_X(center) as lat, ST_Y(center) as lng FROM clusters WHERE cluster_id=:id'''
            result = db.engine.execute(text(query), {"id" : id}).fetchone()
            if (result):
                return jsonify(dict(result)), 200
            else:
                return jsonify({
                    "type": "NotFound",
                    "message": "Data not found for id {0}".format(id)
                }), 404
        else:
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

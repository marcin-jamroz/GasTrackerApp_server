from flask import Flask, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)


@app.route('/')
def home():
    result = db.engine.execute("SELECT network_name FROM gas_stations WHERE station_id=237").fetchone()
    result = dict(result)
    print('----------->', type(result))
    print('----------->', result)
    return ' : '.join(result.popitem()), 200


@app.route('/stations/<id>')
def get_station(id):
    query = '''SELECT * FROM gas_stations WHERE station_id=:id'''
    result = db.engine.execute(text(query), {"id" : id}).fetchone()
    return jsonify(dict(result)), 200


@app.route('/networks', defaults={'id': None})
@app.route('/networks/<id>')
def get_network(id):
    try:
        if (id):
            query = '''SELECT * FROM gas_networks WHERE network_id=:id'''
            result = db.engine.execute(text(query), {"id" : id}).fetchone()
            return jsonify(dict(result)), 200
        else:
            query = '''SELECT * FROM gas_networks'''
            result = db.engine.execute(text(query))
            return jsonify([dict(r) for r in result]), 200
    except Exception as e:
        result = dict()
        result['type'] = type(e).__name__
        result['message'] = e.message if hasattr(e, 'message') else str(e)
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

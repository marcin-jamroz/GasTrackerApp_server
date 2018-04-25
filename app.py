from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy

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
    return ' : '.join(result.popitem()), type(result)


if __name__ == '__main__':
    app.run(debug=True)

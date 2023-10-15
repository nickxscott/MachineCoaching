from flask import Flask, request, jsonify, session
from flask_session import Session

#from datetime import datetime, date
from functions import *
import requests

#flask app
app = Flask(__name__)
app.secret_key = "thisisthesecretkey"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/', methods=['GET','POST'])
def get_cal():
    race_year = int(request.json['year'])
    race_month = int(request.json['month'])
    race_day = int(request.json['day'])
    weeks = int(request.json['weeks'])
    pace_min = int(request.json['min'])
    pace_sec = int(request.json['sec'])
    race_dist = float(request.json['dist'])
    result = get_calendar(race_year=race_year, race_month=race_month, race_day=race_day, weeks=weeks, pace_min=pace_min, pace_sec=pace_sec, race_dist=race_dist)
    cal = result[0]
    raw_level = result[1]
    dist_level = result[2]
    z2 = pace_to_str(result[10])
    mp = pace_to_str(result[9])
    hmp = pace_to_str(result[8])
    ten_k = pace_to_str(result[7])
    five_k = pace_to_str(result[6])
    return result[0].to_json(orient='records', date_format='iso', date_unit='s')

@app.route('/api', methods=['GET','POST'])
def test():
    x = request.json['year']
    return jsonify(x)


if __name__ == '__main__':
  app.run(host='192.168.1.45', port=3000, debug=True)
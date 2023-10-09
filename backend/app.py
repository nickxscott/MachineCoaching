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
    result = get_calendar(race_year=2023, race_month=11, race_day=19, weeks=16, pace_min=7, pace_sec=10, race_dist=26.2)
    raw_level = result[1]
    dist_level = result[2]
    z2 = pace_to_str(result[10])
    mp = pace_to_str(result[9])
    hmp = pace_to_str(result[8])
    ten_k = pace_to_str(result[7])
    five_k = pace_to_str(result[6])
    return jsonify(mp)

@app.route('/api', methods=['GET','POST'])
def test():
    x = request.json['year']
    return jsonify(x)


if __name__ == '__main__':
  app.run(host='192.168.1.45', port=3000, debug=True)
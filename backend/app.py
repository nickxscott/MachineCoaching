from flask import Flask,render_template,request,url_for,flash,jsonify,session,redirect
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

@app.route('/')
def get_cal():
    df = get_calendar(race_year=2023, race_month=11, race_day=19, weeks=16, pace_min=7, pace_sec=10, race_dist=26.2)
    return df


if __name__ == '__main__':
  app.run(debug=True)
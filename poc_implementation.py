import os
import threading
import time
import requests
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Define your database models
class OriginalRecord(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

def init_db(app):
    with app.app_context():
        db.create_all()

def fetch_iss_location():
    response = requests.get("http://api.open-notify.org/iss-now.json")
    data = response.json()
    latitude = float(data['iss_position']['latitude'])
    longitude = float(data['iss_position']['longitude'])
    timestamp = datetime.utcfromtimestamp(data['timestamp'])
    return latitude, longitude, timestamp

def store_iss_location():
    latitude, longitude, timestamp = fetch_iss_location()
    record = OriginalRecord(latitude=latitude, longitude=longitude, timestamp=timestamp)
    db.session.add(record)
    db.session.commit()
    print(f"Stored ISS location: {latitude}, {longitude} at {timestamp}")

def main_loop(app):
    with app.app_context():
        while True:
            store_iss_location()
            time.sleep(60)  # Fetch and store data every 60 seconds

if __name__ == '__main__':
    init_db(app)
    main_thread = threading.Thread(target=main_loop, args=(app,))
    main_thread.daemon = True
    main_thread.start()

    # Keep the script running
    while True:
        time.sleep(1)
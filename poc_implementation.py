import os
import requests
import json
from datetime import datetime
import time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Database model
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

# Data ingestion
def fetch_data():
    response = requests.get('http://api.open-notify.org/iss-now.json')
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

# Data processing
def process_data(raw_data):
    position = raw_data['iss_position']
    timestamp = datetime.fromtimestamp(raw_data['timestamp'])
    return {
        'latitude': float(position['latitude']),
        'longitude': float(position['longitude']),
        'timestamp': timestamp
    }

# Data storage
def store_data(processed_data):
    new_record = Record(**processed_data)
    db.session.add(new_record)
    db.session.commit()

# Simulated remote delivery
def deliver_to_remote(processed_data):
    print(f"Delivering to remote: {processed_data}")

# Main processing loop
def main_loop(app):
    with app.app_context():
        while True:
            try:
                raw_data = fetch_data()
                processed_data = process_data(raw_data)
                store_data(processed_data)
                deliver_to_remote(processed_data)
                time.sleep(5)  # Wait for 5 seconds before next fetch
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                time.sleep(60)  # Wait for a minute before retrying if there's an error

# Authentication
users = {
    "admin": "password"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

# API routes
@app.route('/api/records', methods=['GET'])
@auth.login_required
def get_records():
    records = Record.query.order_by(Record.timestamp.desc()).limit(100).all()
    return jsonify([{
        'id': record.id,
        'latitude': record.latitude,
        'longitude': record.longitude,
        'timestamp': record.timestamp.isoformat()
    } for record in records])

def init_db(app):
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database initialized with new schema.")

if __name__ == '__main__':
    # Check if the database file exists
    if os.path.exists('data.db'):
        # If it exists, remove it
        os.remove('data.db')
        print("Existing database removed.")
    
    # Initialize the database with the new schema
    init_db(app)
    
    # Start the main loop in a separate thread
    thread = threading.Thread(target=main_loop, args=(app,))
    thread.daemon = True
    thread.start()
    
    # Run the Flask application
    app.run(debug=True, use_reloader=False)
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = {
    'enriched': 'sqlite:///enriched_data.db'
}
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory user store for simplicity
users = {
    "admin": "password"
}

@auth.verify_password
def verify_password(username, password):
    logging.info(f"Verifying user: {username}")
    if username in users and users[username] == password:
        logging.info(f"User {username} authenticated successfully")
        return username
    logging.warning(f"User {username} failed authentication")
    return None

# Database model for enriched data
class EnrichedRecord(db.Model):
    __bind_key__ = 'enriched'
    __tablename__ = 'enriched_record'  # Explicitly specify the table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_id = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    enriched_data = db.Column(db.Text, nullable=True)

# Endpoint to retrieve enriched data
@app.route('/enriched_records', methods=['GET'])
@auth.login_required
def get_enriched_records():
    try:
        records = EnrichedRecord.query.all()
        logging.info(f"Fetched {len(records)} enriched records.")
        return jsonify([{
            'id': record.id,
            'original_id': record.original_id,
            'latitude': record.latitude,
            'longitude': record.longitude,
            'timestamp': record.timestamp,
            'enriched_data': record.enriched_data
        } for record in records])
    except Exception as e:
        logging.error(f"Error fetching enriched records: {e}")
        return "Error fetching enriched records", 500

# Endpoint to display enriched data in a web page
@app.route('/display', methods=['GET'])
# @auth.login_required
def display_records():
    try:
        records = EnrichedRecord.query.all()
        logging.info(f"Fetched {len(records)} enriched records.")
        for record in records:
            logging.info(f"Record: {record.id}, {record.original_id}, {record.latitude}, {record.longitude}, {record.timestamp}, {record.enriched_data}")
        return render_template('display.html', records=records)
    except Exception as e:
        logging.error(f"Error fetching enriched records: {e}")
        return "Error fetching enriched records", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all(bind_key='enriched')
    
    # Start the Flask web server on port 5001
    logging.info("Starting Flask server on port 5001")
    app.run(debug=True, port=5001)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import threading
from transformers import pipeline
import time
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = {
    'original': 'sqlite:///data.db',
    'enriched': 'sqlite:///enriched_data.db'
}
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database model for original data
class OriginalRecord(db.Model):
    __bind_key__ = 'original'
    __tablename__ = 'record'  # Ensure this matches the table name in data.db
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

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

# Initialize the model
generator = pipeline('text-generation', model='gpt2')

# Data enrichment
def enrich_data():
    with app.app_context():
        while True:
            logging.info("Starting data enrichment process...")
            original_records = OriginalRecord.query.all()
            if not original_records:
                logging.info("No original records found.")
            for record in original_records:
                # Check if the record has already been enriched
                existing_enriched_record = EnrichedRecord.query.filter_by(original_id=record.id).first()
                if existing_enriched_record:
                    logging.info(f"Record ID {record.id} already enriched.")
                    continue

                prompt = f"The ISS is currently at latitude {record.latitude} and longitude {record.longitude}."
                enriched_data = generator(prompt, max_length=50, num_return_sequences=1, truncation=True)[0]['generated_text']
                
                enriched_record = EnrichedRecord(
                    original_id=record.id,
                    latitude=record.latitude,
                    longitude=record.longitude,
                    timestamp=record.timestamp,
                    enriched_data=enriched_data
                )
                db.session.add(enriched_record)
                try:
                    db.session.commit()
                    logging.info(f"Enriched data saved for record ID {record.id}")
                except Exception as e:
                    db.session.rollback()
                    logging.error(f"Error saving enriched data for record ID {record.id}: {e}")
            
            # Enrich data every 60 seconds
            time.sleep(60)

if __name__ == '__main__':
    with app.app_context():
        db.create_all(bind_key='enriched')
    
    # Start the data enrichment thread
    enrich_thread = threading.Thread(target=enrich_data)
    enrich_thread.daemon = True
    enrich_thread.start()
    
    # Keep the script running
    while True:
        time.sleep(1)
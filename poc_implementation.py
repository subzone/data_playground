import os
import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Define your database models and other setup here

def init_db(app):
    with app.app_context():
        db.create_all()

def main_loop(app):
    with app.app_context():
        while True:
            # Your main loop logic here
            pass

if __name__ == '__main__':
    if not os.path.exists('data.db'):
        # Initialize the database with the new schema
        init_db(app)
        print("Database initialized.")
    else:
        print("Database already exists.")

    # Start the main loop in a separate thread
    thread = threading.Thread(target=main_loop, args=(app,))
    thread.daemon = True
    thread.start()
    
    # Run the Flask application
    app.run(debug=True, use_reloader=False)
# Project data_playground
To address requirements, I'll create a high-level design diagram and provide a basic proof of concept (PoC) for the system you've described. Let's start with the design diagram.

Now, let me explain the components of this high-level design:

## Enriched Data Flow

```mermaid
graph TD
    A[Public Dataset] -->|Fetch hourly| B[Data Ingestion Service]
    B -->|Raw Data| C[Data Lake]
    B -->|Trigger| D[Data Processing Service]
    D -->|Read| C
    D -->|Transform| E[Data Transformation]
    E -->|Processed Data| F[Database]
    E -->|Data Increments| G[Remote Location]
    H[REST API Service] -->|Read/Write| F
    I[Authentication Service] --> H
    J[Monitoring Service] -->|Monitor| B
    J -->|Monitor| D
    J -->|Monitor| F
    K[Backfill Service] -->|Detect & Fix| C
    K -->|Detect & Fix| F
```

Data Ingestion Service: Fetches data from the public dataset hourly.
Data Lake: Stores raw data for backup and potential reprocessing.
Data Processing Service: Transforms the data according to business logic.
Database: Stores unique, processed records.
Remote Location: Receives incremental data updates.
REST API Service: Provides authenticated access to the database.
Authentication Service: Handles user authentication for the API.
Monitoring Service: Monitors the system for issues and delays.
Backfill Service: Detects and fixes data corruption or gaps.

For a working PoC, I implemented a simplified version of this system using Python. I'll focus on the core components: data ingestion, processing, storage, and API access.

###################################################################

This PoC implements the core functionality of the system:

Data Ingestion: The fetch_data() function simulates fetching data from a public API.
Data Processing: process_data() transforms the raw data by adding a timestamp.
Data Storage: store_data() saves the processed data to a SQLite database.
Remote Delivery: deliver_to_remote() simulates sending data to a remote location.
API Access: A Flask app provides an authenticated REST API to access the stored records.

###################################################################

To run this PoC:
need python and venv

activate venv

```sh
venv\Scripts\activate 
```

Install the required packages: 

```sh
pip install -r requirements.txt
```

or run appropriate setup (bat or sh)

This will install simple script to fetch data on ISS position longitude/latitude and timestamp.


Run the script. It will start the Flask server and begin the data processing loop.
Access the API at http://localhost:5000/api/records using Basic Auth with username "admin" and password "password".


####################################################################
GPT2 enricher

Added a small function to enrich data and store in additional db, for PoC should be enough, can be same db, diff table, same table depending on actual use case...
Now, I do not have available any OpenAI or similar API that I am paying so this enrichment is limited to GPT2...

to run it:

```sh
py enrich_data.py
```

to see data in browser and access enriched data:

```sh
py display_data.py
```

####################################################################

This PoC doesn't implement all features (like backfilling or extensive error handling) but demonstrates the core functionality. In a production environment, you'd need to:

Use a more robust database like PostgreSQL.
Implement proper error handling and logging.
Use a production-ready web server.
Implement a more secure authentication system.
Use a task queue (like Celery) for background processing.
Implement the backfill service to handle data corruption and gaps.
Set up monitoring and alerting for system health and performance.
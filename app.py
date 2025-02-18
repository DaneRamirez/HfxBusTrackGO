# app.py

# Import Flask and related functions to create our web server
from flask import Flask, jsonify, send_from_directory
# Import requests to fetch external data from HFX Transit
import requests
# Import the generated Protocol Buffers classes (from gtfs-realtime.proto)
import gtfs_realtime_pb2

# Create a new Flask application instance
app = Flask(__name__)


# -----------------------------------------------------------------------------
# ROUTE: Serve the Frontend HTML File
# -----------------------------------------------------------------------------
@app.route('/')
def index():
    """
    Serve the index.html file located in the 'static' directory.
    This HTML file contains our frontend code (map, JavaScript, etc.).
    """
    return send_from_directory('static', 'index.html')  # Serve index.html from 'static' folder


# -----------------------------------------------------------------------------
# ROUTE: API Endpoint to Provide Bus Position Data
# -----------------------------------------------------------------------------
@app.route('/api/positions', methods=['GET'])
def get_positions():
    """
    This function performs the following steps:
      1. Fetches the GTFS-realtime vehicle positions from HFX Transit.
      2. Parses the Protocol Buffers (.pb) data using our generated classes.
      3. Extracts the following information for each vehicle:
         - Nested vehicle id and label (from vehicle.vehicle)
         - Bus route (vehicle.trip.route_id)
         - Timestamp (vehicle.timestamp)
         - Direction ID (vehicle.trip.direction_id)
         - Start date (vehicle.trip.start_date)
         - GPS position (latitude, longitude, and optionally speed)
      4. Returns the extracted data as a JSON array.
    """
    # URL for the GTFS-realtime Vehicle Positions .pb file from HFX Transit
    url = "https://gtfs.halifax.ca/realtime/Vehicle/VehiclePositions.pb"

    # Fetch the data using requests with verify=False as a temporary workaround for SSL issues
    response = requests.get(url, verify=False)

    # If the request did not succeed, return an error message with the HTTP status code
    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve data", "status_code": response.status_code}), 500

    # Create an instance of FeedMessage (the top-level message in the GTFS-realtime schema)
    feed_message = gtfs_realtime_pb2.FeedMessage()
    # Parse the binary Protocol Buffers data into the feed_message object
    feed_message.ParseFromString(response.content)

    # Create an empty list to store bus information dictionaries
    positions = []

    # Loop over each entity in the feed_message (each entity represents a bus or alert)
    for entity in feed_message.entity:
        # Check if the entity has a 'vehicle' field
        if entity.HasField('vehicle'):
            # Access the vehicle information from the entity
            vehicle_info = entity.vehicle

            # Extract the nested vehicle id and label from the inner 'vehicle' field
            bus_id = vehicle_info.vehicle.id  # Example: "3410"
            bus_label = vehicle_info.vehicle.label  # Example: "1410"

            # Initialize variables for GPS position data
            latitude = None
            longitude = None
            speed = None

            # Check if the vehicle_info contains the 'position' field and extract data
            if vehicle_info.HasField('position'):
                latitude = vehicle_info.position.latitude
                longitude = vehicle_info.position.longitude
                # 'speed' is optional so we check for its existence
                if vehicle_info.position.HasField('speed'):
                    speed = vehicle_info.position.speed

            # Initialize variables for trip data
            route_id = None
            direction_id = None
            start_date = None

            # Check if the vehicle_info has a 'trip' field
            if vehicle_info.HasField('trip'):
                # Access the trip information
                trip_info = vehicle_info.trip
                route_id = trip_info.route_id  # Example: "22"
                # direction_id may be optional; assign if available
                if trip_info.HasField('direction_id'):
                    direction_id = trip_info.direction_id
                start_date = trip_info.start_date  # Example: "20250217"

            # Extract the vehicle timestamp from the top-level vehicle_info (not inside trip)
            timestamp = vehicle_info.timestamp  # Example: 1739828851

            # Append all extracted information into the positions list as a dictionary
            positions.append({
                "vehicle_id": bus_id,  # Nested vehicle id
                "vehicle_label": bus_label,  # Nested vehicle label
                "route_id": route_id,  # Bus route number (from trip)
                "timestamp": timestamp,  # Timestamp of the data
                "direction_id": direction_id,  # Direction of the bus (from trip)
                "start_date": start_date,  # Service start date (from trip)
                "latitude": latitude,  # GPS latitude
                "longitude": longitude,  # GPS longitude
                "speed": speed  # GPS speed (if available)
            })

    # Return the list of bus positions as a JSON response
    return jsonify(positions)


# -----------------------------------------------------------------------------
# MAIN: Run the Flask Application Securely Using a Self-Signed Certificate
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # The app runs on HTTPS on port 5000 using our self-signed certificate files:
    # - cert.pem: The certificate file
    # - key.pem: The private key file
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))

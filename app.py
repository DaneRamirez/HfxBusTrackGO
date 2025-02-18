# app.py

# Import Flask to create our web application
from flask import Flask, jsonify, send_from_directory
# Import requests to make HTTP requests
import requests
# Import the generated protobuf classes from the .proto file
import gtfs_realtime_pb2

# Create a new Flask application instance
app = Flask(__name__)


# Route to serve our index.html file (frontend)
@app.route('/')
def index():
    # Serve the index.html file located in the 'static' folder
    return send_from_directory('static', 'static/index.html')  # 'static' folder must contain index.html


# API endpoint to return vehicle positions as JSON
@app.route('/api/positions', methods=['GET'])
def get_positions():
    """
    This function fetches the GTFS-realtime vehicle positions data,
    decodes the Protocol Buffers (.pb) data into a FeedMessage,
    extracts the required vehicle information,
    and returns it as JSON.
    """
    # URL for the GTFS-realtime Vehicle Positions .pb file
    url = "https://gtfs.halifax.ca/realtime/Vehicle/VehiclePositions.pb"

    # Fetch the .pb data using requests. Note: we are using verify=False
    # to bypass SSL verification (not recommended for production).
    response = requests.get(url, verify=False)

    # Check if the request succeeded (HTTP status code 200)
    if response.status_code != 200:
        # If not successful, return an error message and status code as JSON
        return jsonify({"error": "Failed to retrieve data", "status_code": response.status_code}), 500

    # Create an instance of FeedMessage (the top-level message from gtfs_realtime_pb2)
    feed_message = gtfs_realtime_pb2.FeedMessage()
    # Parse the binary data into the feed_message object
    feed_message.ParseFromString(response.content)

    # Initialize an empty list to store our vehicle positions
    positions = []

    # Loop through each entity in the feed_message (each entity represents a vehicle or alert)
    for entity in feed_message.entity:
        # Check if the entity contains vehicle data
        if entity.HasField('vehicle'):
            # Access the vehicle field from the entity
            vehicle_info = entity.vehicle

            # The structure of the message is such that vehicle_info contains a nested 'vehicle'
            # that holds the vehicle id and label.
            # We extract them as follows:
            bus_id = vehicle_info.vehicle.id  # Nested vehicle id
            bus_label = vehicle_info.vehicle.label  # Nested vehicle label

            # Initialize variables for position data
            latitude = None
            longitude = None
            speed = None

            # Check if there is a 'position' field within vehicle_info
            if vehicle_info.HasField('position'):
                latitude = vehicle_info.position.latitude  # Get latitude
                longitude = vehicle_info.position.longitude  # Get longitude
                # 'speed' is optional, so check if it exists before accessing
                if vehicle_info.position.HasField('speed'):
                    speed = vehicle_info.position.speed

            # Append a dictionary with the extracted data to the positions list
            positions.append({
                "vehicle_id": bus_id,  # Bus identifier from the nested field
                "vehicle_label": bus_label,  # Bus label
                "latitude": latitude,  # Bus latitude
                "longitude": longitude,  # Bus longitude
                "speed": speed  # Bus speed (if available)
            })

    # Return the positions list as a JSON response
    return jsonify(positions)


# Only run the Flask application if this script is executed directly
if __name__ == '__main__':
    # Run the Flask app on all available addresses (0.0.0.0) on port 5000
    # We run it using HTTPS with our self-signed certificate (cert.pem and key.pem)
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))

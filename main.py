import requests
import gtfs_realtime_pb2

# Fetch the .pb data
url = 'https://gtfs.halifax.ca/realtime/Vehicle/VehiclePositions.pb'
response = requests.get(url, verify=False) #temporarily disable ssl certification.

if response.status_code == 200:
    # Deserialize the .pb data into a FeedMessage object
    feed_message = gtfs_realtime_pb2.FeedMessage()
    feed_message.ParseFromString(response.content)

    # Loop through the entities and print their structure
    for entity in feed_message.entity:
        print(f"Entity: {entity}")

        # Print each entity's vehicle information
        if entity.HasField('vehicle'):
            vehicle = entity.vehicle
            print(f"Vehicle: {vehicle}")


            print(f"Vehicle ID: {vehicle.vehicle.id}")
            print(f"Vehicle Label: {vehicle.vehicle.label}")

            # Access position and other information if available
            if vehicle.HasField('position'):
                position = vehicle.position
                print(f"Latitude: {position.latitude}")
                print(f"Longitude: {position.longitude}")
                print(f"Speed: {position.speed}")
        else:
            print("No vehicle data found in this entity.")
else:
    print(f"Failed to fetch data: {response.status_code}")

from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API keys from environment variables
OPEN_CHARGE_API_KEY = os.getenv('OPEN_CHARGE_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# API URLs
GOOGLE_MAPS_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
OPEN_CHARGE_API_URL = "https://api.openchargemap.io/v3/poi"

@app.route('/')
def index():
    """Render the homepage with search inputs."""
    return render_template('index.html', google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/search', methods=['POST'])
def search_route():
    """Handle search and fetch route with charging stations."""
    # Get user inputs
    from_location = request.form['from']
    to_location = request.form['to']

    # Fetch the route using Google Maps Directions API
    route = get_route(from_location, to_location)

    if not route:
        return render_template('stations.html', route=[], stations=[], from_location=from_location, to_location=to_location)

    # Find charging stations along the route
    stations = get_stations_along_route(route)

    # Render the results page with route and stations
    return render_template('stations.html', route=route, stations=stations, from_location=from_location, to_location=to_location)

def get_route(from_location, to_location):
    """Fetch the route between two locations using Google Maps Directions API."""
    params = {
        'origin': from_location,
        'destination': to_location,
        'key': GOOGLE_MAPS_API_KEY,
    }
    response = requests.get(GOOGLE_MAPS_DIRECTIONS_URL, params=params)
    data = response.json()

    if data.get('status') == 'OK':
        steps = []
        for leg in data['routes'][0]['legs']:
            for step in leg['steps']:
                lat = step['end_location']['lat']
                lng = step['end_location']['lng']
                steps.append({'lat': lat, 'lng': lng})
        return steps
    return None

def get_stations_along_route(route):
    """Fetch charging stations along the route using Open Charge Map API."""
    stations = []
    for point in route:
        params = {
            'latitude': point['lat'],
            'longitude': point['lng'],
            'distance': 15,  # Search within 5 km radius
            'maxresults': 20,  # Limit results per step
            'key': OPEN_CHARGE_API_KEY,
        }
        response = requests.get(OPEN_CHARGE_API_URL, params=params)
        if response.status_code == 200:
            stations.extend(response.json())
        else:
            print(f"Error fetching stations for {point['lat']}, {point['lng']}")

    if not stations:
        print("No stations found.")
    else:
        print(f"Found {len(stations)} stations")

    return format_stations(stations)

def format_stations(stations):
    """Format charging station data for rendering."""
    formatted = []
    for station in stations:
        formatted.append({
            'name': station.get('AddressInfo', {}).get('Title', 'Unknown'),
            'address': station.get('AddressInfo', {}).get('AddressLine1', 'Unknown'),
            'distance': station.get('AddressInfo', {}).get('Distance', 'Unknown'),
            'status': station.get('StatusType', {}).get('Title', 'Unknown'),
            'charger_type': station.get('Connections', [{}])[0].get('ConnectionType', {}).get('Title', 'Unknown'),
            'lat': station.get('AddressInfo', {}).get('Latitude', 0),
            'lng': station.get('AddressInfo', {}).get('Longitude', 0),
        })
    return formatted

if __name__ == '__main__':
    app.run(debug=True)

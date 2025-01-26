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

# Google Maps Geocoding API URL
GOOGLE_MAPS_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Open Charge Map API URL
OPEN_CHARGE_API_URL = "https://api.openchargemap.io/v3/poi"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_stations():
    # Get the 'from' and 'to' locations from the form
    from_location = request.form['from']
    to_location = request.form['to']

    # Get latitudes and longitudes for the locations using Google Maps Geocoding API
    from_coords = get_coordinates(from_location)
    to_coords = get_coordinates(to_location)

    if from_coords and to_coords:
        # Fetch nearby charging stations using Open Charge Map API
        stations = get_nearby_stations(from_coords, to_coords)
        return render_template('stations.html', stations=stations, from_location=from_location, to_location=to_location)
    else:
        return "Error: Unable to get coordinates."

def get_coordinates(location):
    """Fetches the latitude and longitude for a location using Google Maps Geocoding API"""
    params = {
        'address': location,
        'key': GOOGLE_MAPS_API_KEY
    }
    response = requests.get(GOOGLE_MAPS_GEOCODE_URL, params=params)
    data = response.json()

    if data['status'] == 'OK':
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
        return {'lat': lat, 'lng': lng}
    return None

def get_nearby_stations(from_coords, to_coords):
    """Fetches nearby charging stations using the Open Charge Map API"""
    params = {
        'latitude': from_coords['lat'],
        'longitude': from_coords['lng'],
        'distance': 50,  # 50 km radius
        'maxresults': 10,  # Limit results to 10 stations
        'key': OPEN_CHARGE_API_KEY
    }
    response = requests.get(OPEN_CHARGE_API_URL, params=params)
    stations = response.json()

    # Format stations data
    formatted_stations = []
    for station in stations:
        station_info = {
            'name': station.get('AddressInfo', {}).get('Title', 'N/A'),
            'address': station.get('AddressInfo', {}).get('AddressLine1', 'N/A'),
            'distance': station.get('AddressInfo', {}).get('Distance', 'N/A'),
            'status': station.get('StatusType', {}).get('Title', 'N/A'),
            'charger_type': station.get('Connections', [{}])[0].get('ConnectionType', {}).get('Title', 'N/A')
        }
        formatted_stations.append(station_info)

    return formatted_stations

if __name__ == '__main__':
    app.run(debug=True)

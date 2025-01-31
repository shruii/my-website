import requests
from flask import Flask, render_template, request
from geopy.distance import geodesic
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get API keys from environment variables
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
OPEN_CHARGE_API_KEY = os.getenv('OPEN_CHARGE_API_KEY')

# Vehicle range dictionary (assumed ranges in km for simplicity)
vehicle_ranges = {
    'Model X': 500,
    'Model Y': 450,
    'Tata Nexon': 312,
    'Mahindra e2o': 140
}

@app.route('/')
def home():
    return render_template('index.html', google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/search', methods=['POST'])
def search():
    from_location = request.form['from']
    to_location = request.form['to']
    vehicle_model = request.form['vehicle_model']
    battery_level = int(request.form['battery_level'])
    charger_type = request.form['charger_type']
    station_status = request.form['station_status']

    # Fetch multiple routes
    routes = get_route(from_location, to_location)
    if not routes:
        return "Error: Could not fetch routes. Please check your input and try again."

    # For simplicity, use the first route
    selected_route = routes[0]['route']
    charging_stations = get_charging_stations(selected_route)

    # Estimate remaining range
    estimated_range = estimate_range(vehicle_model, battery_level)
    return render_template('route.html', routes=routes, selected_route=selected_route, stations=charging_stations, estimated_range=estimated_range, google_maps_api_key=GOOGLE_MAPS_API_KEY)

def get_route(from_location, to_location):
    # Get multiple routes from Google Maps Directions API
    params = {
        'origin': from_location,
        'destination': to_location,
        'alternatives': 'true',  # Fetch alternative routes
        'key': GOOGLE_MAPS_API_KEY,
    }
    try:
        response = requests.get('https://maps.googleapis.com/maps/api/directions/json', params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'OK':
            routes = []
            for route in data['routes']:
                total_distance = 0
                total_duration = 0
                steps = []
                for leg in route['legs']:
                    total_distance += leg['distance']['value']
                    total_duration += leg['duration']['value']
                    for step in leg['steps']:
                        lat = step['end_location']['lat']
                        lng = step['end_location']['lng']
                        steps.append({'lat': lat, 'lng': lng})
                routes.append({
                    'distance': total_distance,
                    'duration': total_duration,
                    'route': steps,
                })
            return routes
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching route: {e}")
        return None

def get_charging_stations(route):
    stations = []
    for point in route:
        params = {
            'location': f"{point['lat']},{point['lng']}",
            'radius': 5000,  # Search radius in meters (5 km)
            'type': 'electric_vehicle_charging_station',
            'key': GOOGLE_MAPS_API_KEY,
        }
        try:
            response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'OK':
                for place in data['results']:
                    station = {
                        'name': place.get('name', 'Unknown'),
                        'address': place.get('vicinity', 'Unknown'),
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'rating': place.get('rating', 'N/A'),
                        'distance': calculate_distance_from_route({'lat': place['geometry']['location']['lat'], 'lng': place['geometry']['location']['lng']}, route)
                    }
                    stations.append(station)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching charging stations: {e}")
    return stations

def calculate_distance_from_route(station, route):
    station_coords = (station['lat'], station['lng'])
    route_coords = [(point['lat'], point['lng']) for point in route]
    min_distance = min([geodesic(station_coords, point).km for point in route_coords])
    return round(min_distance, 2)

def estimate_range(vehicle_model, battery_level):
    max_range = vehicle_ranges.get(vehicle_model, 0)
    estimated_range = (battery_level / 100) * max_range
    return round(estimated_range, 2)

if __name__ == '__main__':
    app.run(debug=True)
# app.py
import requests
from flask import Flask, render_template, request, jsonify
from geopy.distance import geodesic
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import polyline

load_dotenv()

app = Flask(__name__)

GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
OPEN_CHARGE_API_KEY = os.getenv('OPEN_CHARGE_API_KEY')

# Vehicle range dictionary (in km)
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
    data = request.form
    from_location = data['from']
    to_location = data['to']
    vehicle_model = data['vehicle_model']
    battery_level = int(data['battery_level'])

    # Get multiple routes
    routes = get_routes(from_location, to_location)
    if not routes:
        return "Error: Could not fetch routes. Please check your input and try again."

    # Calculate estimated range
    estimated_range = (battery_level / 100) * vehicle_ranges[vehicle_model]

    # Get charging stations for each route
    for route in routes:
        route['charging_stations'] = get_combined_charging_stations(route['points'])

    return render_template('route.html', 
                         routes=routes,
                         estimated_range=estimated_range,
                         from_location=from_location,
                         to_location=to_location,
                         google_maps_api_key=GOOGLE_MAPS_API_KEY)

def get_routes(from_location, to_location):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin': from_location,
        'destination': to_location,
        'alternatives': 'true',
        'key': GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] != 'OK':
            return None

        routes = []
        for i, route in enumerate(data['routes']):
            points = []
            path = []
            distance = 0
            duration = 0

            for leg in route['legs']:
                distance += leg['distance']['value']
                duration += leg['duration']['value']
                
                # Get points along the route for charging station search
                for step in leg['steps']:
                    points.append({
                        'lat': step['end_location']['lat'],
                        'lng': step['end_location']['lng']
                    })
                    path.append(step['polyline']['points'])

            routes.append({
                'id': i,
                'points': points,
                'path': path,
                'distance': round(distance / 1000, 2),  # Convert to km
                'duration': round(duration / 60),  # Convert to minutes
                'charging_stations': []
            })

        return routes
    except Exception as e:
        print(f"Error fetching routes: {e}")
        return None

def get_combined_charging_stations(route_points):
    stations = []
    seen_stations = set()  # To track unique stations

    # Sample points along the route to search for stations
    # Take every 5th point, but ensure at least 5 and at most 20 sample points
    step = max(1, len(route_points) // 10)
    sample_points = route_points[::step]
    if len(sample_points) > 20:
        sample_points = sample_points[:20]
    
    for point in sample_points:
        # Get stations from Google Places API
        google_stations = get_google_charging_stations(point)
        
        # Get stations from Open Charge Map API
        ocm_stations = get_ocm_charging_stations(point)

        # Combine stations from both sources
        for station in google_stations + ocm_stations:
            station_id = f"{station['lat']}-{station['lng']}"
            if station_id not in seen_stations:
                seen_stations.add(station_id)
                stations.append(station)

    return stations

def get_google_charging_stations(point):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{point['lat']},{point['lng']}",
        'radius': 5000,  # 5km radius
        'keyword': 'EV charging station',  # Add keyword for better results
        'type': 'electric_vehicle_charging_station',
        'key': GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        stations = []
        if data.get('status') == 'OK':
            for place in data['results']:
                # Verify this is actually an EV charging station by checking name/types
                name = place.get('name', '').lower()
                types = [t.lower() for t in place.get('types', [])]
                
                is_ev_station = (
                    'charge' in name or 
                    'charging' in name or 
                    'ev' in name or 
                    'electric' in name or
                    'electric_vehicle_charging_station' in types
                )
                
                if is_ev_station:
                    stations.append({
                        'source': 'google',
                        'name': place.get('name', 'Unknown Station'),
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'address': place.get('vicinity', 'Address not available'),
                        'rating': place.get('rating', 'N/A'),
                        'is_operational': place.get('business_status', '') == 'OPERATIONAL'
                    })
        return stations
    except Exception as e:
        print(f"Error fetching Google charging stations: {e}")
        return []

def get_ocm_charging_stations(point):
    url = "https://api.openchargemap.io/v3/poi"
    params = {
        'key': OPEN_CHARGE_API_KEY,
        'latitude': point['lat'],
        'longitude': point['lng'],
        'distance': 5,  # 5km radius
        'distanceunit': 'km',
        'maxresults': 10,
        'compact': True,
        'verbose': False,
        'operationalstatus': 'Operational'  # Only get operational stations
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        stations = []
        for station in data:
            # Skip stations with no connection data
            connections = station.get('Connections', [])
            if not connections:
                continue
                
            power_levels = [conn.get('PowerKW', 0) for conn in connections if conn.get('PowerKW')]
            max_power = max(power_levels) if power_levels else 0
            
            # Get connector types
            connector_types = []
            for conn in connections:
                conn_type = conn.get('ConnectionType', {}).get('Title')
                if conn_type and conn_type not in connector_types:
                    connector_types.append(conn_type)
            
            # Only include stations with at least one connector type
            if connector_types:
                stations.append({
                    'source': 'ocm',
                    'name': station.get('AddressInfo', {}).get('Title', 'Unknown Station'),
                    'lat': station.get('AddressInfo', {}).get('Latitude'),
                    'lng': station.get('AddressInfo', {}).get('Longitude'),
                    'address': station.get('AddressInfo', {}).get('AddressLine1', 'Address not available'),
                    'power_kw': max_power,
                    'is_operational': station.get('StatusType', {}).get('IsOperational', True),
                    'connectors': connector_types
                })
        return stations
    except Exception as e:
        print(f"Error fetching OCM charging stations: {e}")
        return []

if __name__ == '__main__':
    app.run(debug=True)
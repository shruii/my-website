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

<<<<<<< HEAD
# Vehicle range dictionary (in km)
vehicle_ranges = {
    'Model X': 500,
    'Model Y': 450,
    'Tata Nexon': 312,
    'Mahindra e2o': 140
=======
vehicle_database = {
    'Tata Nexon': {
        'range': 312,
        'battery_capacity': 30.2,
        'charging_speed_dc': 50,
        'charging_speed_ac': 7.2,
    },
    'Mahindra e2o': {
        'range': 140,
        'battery_capacity': 15.44,
        'charging_speed_dc': 30,
        'charging_speed_ac': 3.3,
    }
>>>>>>> 6eb94df282b107edf8005cf9b75ea824d8ad3bbf
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

<<<<<<< HEAD
    # Get multiple routes
=======
    # Fetch multiple routes
>>>>>>> 6eb94df282b107edf8005cf9b75ea824d8ad3bbf
    routes = get_routes(from_location, to_location)
    if not routes:
        return "Error: Could not fetch routes. Please check your input and try again."

<<<<<<< HEAD
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
=======
    # Initial estimated range calculation
    estimated_range = estimate_range(vehicle_model, battery_level)

    return render_template('routes.html', 
                         routes=routes,
                         estimated_range=estimated_range,
                         google_maps_api_key=GOOGLE_MAPS_API_KEY,
                         from_location=from_location,
                         to_location=to_location)

@app.route('/get_stations', methods=['POST'])
def get_stations():
    data = request.json
    route_points = data['route']

    stations = get_charging_stations(route_points)
    return jsonify({'stations': stations})

@app.route('/station_details/<station_id>')
def station_details(station_id):
    # Fetch detailed station information from your database or API
    station = get_station_details(station_id)
    return jsonify(station)

def get_routes(from_location, to_location):
>>>>>>> 6eb94df282b107edf8005cf9b75ea824d8ad3bbf
    params = {
        'origin': from_location,
        'destination': to_location,
        'alternatives': 'true',
<<<<<<< HEAD
        'key': GOOGLE_MAPS_API_KEY
=======
        'key': GOOGLE_MAPS_API_KEY,
>>>>>>> 6eb94df282b107edf8005cf9b75ea824d8ad3bbf
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

<<<<<<< HEAD
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
    sample_points = route_points[::5]  # Take every 5th point to reduce API calls

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
        'verbose': False
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        stations = []
        for station in data:
            connections = station.get('Connections', [])
            power_levels = [conn.get('PowerKW', 0) for conn in connections if conn.get('PowerKW')]
            max_power = max(power_levels) if power_levels else 0

            stations.append({
                'source': 'ocm',
                'name': station.get('AddressInfo', {}).get('Title', 'Unknown Station'),
                'lat': station.get('AddressInfo', {}).get('Latitude'),
                'lng': station.get('AddressInfo', {}).get('Longitude'),
                'address': station.get('AddressInfo', {}).get('AddressLine1', 'Address not available'),
                'power_kw': max_power,
                'is_operational': station.get('StatusType', {}).get('IsOperational', True),
                'connectors': [conn.get('ConnectionType', {}).get('Title') for conn in connections]
            })
        return stations
    except Exception as e:
        print(f"Error fetching OCM charging stations: {e}")
        return []
=======
        if data.get('status') == 'OK':
            routes = []
            for i, route in enumerate(data['routes']):
                route_info = {
                    'id': f'route_{i}',
                    'points': [],
                    'distance': 0,
                    'duration': 0,
                    'bounds': route['bounds'],
                    'overview_polyline': route['overview_polyline']['points']
                }

                for leg in route['legs']:
                    route_info['distance'] += leg['distance']['value']
                    route_info['duration'] += leg['duration']['value']
                    for step in leg['steps']:
                        route_info['points'].append({
                            'lat': step['end_location']['lat'],
                            'lng': step['end_location']['lng']
                        })

                route_info['distance_text'] = f"{route_info['distance']/1000:.1f} km"
                route_info['duration_text'] = f"{route_info['duration']//3600}h {(route_info['duration']%3600)//60}m"
                routes.append(route_info)

            return routes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching routes: {e}")
        return None

def get_charging_stations(route_points):
    stations = []
    checked_locations = set()  # To avoid duplicate stations

    for point in route_points:
        location_key = f"{point['lat']:.3f},{point['lng']:.3f}"
        if location_key in checked_locations:
            continue

        checked_locations.add(location_key)

        params = {
            'location': f"{point['lat']},{point['lng']}",
            'radius': 5000,  # 5km radius
            'type': 'electric_vehicle_charging_station',
            'key': GOOGLE_MAPS_API_KEY,
        }

        try:
            response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'OK':
                for place in data['results']:
                    station_id = place['place_id']
                    if not any(s['id'] == station_id for s in stations):  # Avoid duplicates
                        station = {
                            'id': station_id,
                            'name': place.get('name', 'Unknown Station'),
                            'address': place.get('vicinity', 'Unknown Location'),
                            'lat': place['geometry']['location']['lat'],
                            'lng': place['geometry']['location']['lng'],
                            'rating': place.get('rating', 'N/A'),
                            'user_ratings_total': place.get('user_ratings_total', 0),
                            'is_operational': place.get('business_status', 'OPERATIONAL') == 'OPERATIONAL',
                        }
                        stations.append(station)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching charging stations: {e}")

    return stations

def get_station_details(station_id):
    params = {
        'place_id': station_id,
        'fields': 'name,rating,formatted_phone_number,formatted_address,opening_hours,website,photo,review',
        'key': GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'OK':
            result = data['result']
            return {
                'id': station_id,
                'name': result.get('name', 'Unknown Station'),
                'address': result.get('formatted_address', 'Unknown Location'),
                'phone': result.get('formatted_phone_number', 'N/A'),
                'rating': result.get('rating', 'N/A'),
                'website': result.get('website', ''),
                'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
                'reviews': result.get('reviews', [])
            }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching station details: {e}")
    return None

def estimate_range(vehicle_model, battery_level):
    vehicle = vehicle_database.get(vehicle_model)
    if not vehicle:
        return 0
    return round((battery_level / 100) * vehicle['range'], 2)
>>>>>>> 6eb94df282b107edf8005cf9b75ea824d8ad3bbf

if __name__ == '__main__':
    app.run(debug=True)
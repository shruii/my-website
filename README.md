# ChargeRoute - EV Charging Route Optimizer

ChargeRoute is a web application designed to optimize the routing of EV charging stations for long-distance travel in India. It provides users with an efficient and user-friendly interface to locate charging stations along their route, ensuring a smooth travel experience.

## Features

- **Interactive Map Interface**: Displays EV charging stations along the user's selected route using Google Maps API.
- **Search & Routing**: Users can input their starting and destination locations to get an optimized route with charging stations.
- **Filtering Options**: Sort charging stations by distance, reviews, and other user preferences.
- **Battery Alerts & Notifications**: Provides notifications for low battery, suggesting the nearest charging station.
- **New Charging Station Suggestions**: Analyzes user feedback and route data to recommend new charging station locations.
- **Nearby Amenities**: Recommends nearby restaurants, restrooms, and tourist spots at charging station stops.
- **EV Servicing Centers**: Displays nearby EV servicing centers for repairs and maintenance.
- **Future Mobile App Integration**: Plans to integrate with EV models for vehicle-specific details and connectivity.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (Google Maps API integration)
- **Backend**: Python (Flask framework)
- **APIs Used**:
  - Google Maps API (Routing & Geolocation)
  - Open Charge Map API (EV Charging Station Data)
  - NREL API (Alternative Fuel Station Data)
- **Database**: (To be determined for user preferences and feedback storage)
- **Hosting**: (To be determined)

## Installation & Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/ChargeRoute.git
   cd ChargeRoute
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables for API keys:
   - `GOOGLE_MAPS_API_KEY`
   - `OPEN_CHARGE_MAP_API_KEY`
   - `NREL_API_KEY`
5. Run the Flask server:
   ```sh
   python app.py
   ```
6. Open `http://127.0.0.1:5000/` in your browser to access the application.

## Future Enhancements

- Mobile app development with enhanced features.
- Integration with EV manufacturers like Ather and Tata for real-time vehicle updates.
- Machine learning-based predictive analytics for route optimization.
- Cloud-based hosting for scalability.

## Contributing

Contributions are welcome! If you have any suggestions or would like to contribute, please submit a pull request.

## License

This project is licensed under the MIT License. See `LICENSE` for more details.

## Contact

For any inquiries or collaborations, contact [your email or GitHub profile].


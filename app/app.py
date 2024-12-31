import os
from flask import Flask, request, jsonify
import requests
import logging
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# URL for the Weather Fetching Service
FETCH_SERVICE_URL = os.getenv("WEATHER_FETCH_SERVICE_URL", "http://weather-fetch-service.weather-wizard.svc.cluster.local/weather")

# Validate critical environment variables
def validate_environment():
    if not FETCH_SERVICE_URL:
        logger.error("Environment variable WEATHER_FETCH_SERVICE_URL is not set.")
        raise RuntimeError("Critical environment variable WEATHER_FETCH_SERVICE_URL is not set.")

validate_environment()

# Configure session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))

@app.before_request
def log_request_info():
    logger.info(json.dumps({
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "body": request.get_json(silent=True)
    }))

@app.after_request
def log_response_info(response):
    logger.info(json.dumps({
        "status_code": response.status_code,
        "response_body": response.get_json(silent=True)
    }))
    return response

@app.route('/analyze', methods=['POST'])
def analyze_weather():
    city = request.json.get("city")
    if not city:
        return jsonify({"error": "City is required."}), 400

    try:
        # Call Weather Fetching Service
        response = session.get(f"{FETCH_SERVICE_URL}?city={city}", timeout=5)
        response.raise_for_status()
        weather_data = response.json()

        # Extract and analyze data
        temperature = weather_data.get("temperature")
        weather = weather_data.get("weather")
        wind_speed = weather_data.get("wind_speed")

        insights = []
        if temperature > 25:
            insights.append("It's a warm day. Stay hydrated!")
        elif temperature < 10:
            insights.append("It's quite cold. Wear warm clothing.")

        if "rain" in weather.lower():
            insights.append("Carry an umbrella; it might rain.")

        if wind_speed > 20:
            insights.append("It's windy. Be cautious outdoors.")

        return jsonify({
            "temperature": temperature,
            "weather": weather,
            "wind_speed": wind_speed,
            "insights": insights
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch weather data: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Check connectivity to Weather Fetching Service
        response = session.get(FETCH_SERVICE_URL, timeout=2)
        response.raise_for_status()
        return jsonify({"status": "healthy"}), 200
    except requests.exceptions.RequestException:
        return jsonify({"status": "unhealthy", "error": "Cannot reach Weather Fetching Service"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

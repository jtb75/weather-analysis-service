# Weather Analysis Service

The **Weather Analysis Service** is a microservice that provides actionable insights based on weather data. It processes temperature, weather conditions, and wind speed to offer recommendations, such as "Carry an umbrella" or "Wear warm clothing."

## Features

- Accepts weather data via a REST API.
- Returns insights and recommendations based on the provided data.
- Health check endpoint for monitoring service status.

---

## Endpoints

### **Health Check**
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Returns the health status of the service.
- **Response**:
  ```json
  {
    "status": "healthy"
  }

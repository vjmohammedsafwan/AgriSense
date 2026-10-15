import urllib.request
import json

# Pre-defined major agricultural hubs / coordinates for quick 1-click selection
CITIES_GEO = {
    "Punjab (Ludhiana)": {"lat": 30.9010, "lon": 75.8573},
    "Haryana (Karnal)": {"lat": 29.6857, "lon": 76.9905},
    "Uttar Pradesh (Varanasi)": {"lat": 25.3176, "lon": 82.9739},
    "Maharashtra (Nashik)": {"lat": 19.9975, "lon": 73.7898},
    "Karnataka (Bengaluru Rural)": {"lat": 13.0827, "lon": 77.5877},
    "Tamil Nadu (Coimbatore)": {"lat": 11.0168, "lon": 76.9558},
    "Gujarat (Anand)": {"lat": 22.5645, "lon": 72.9289},
    "West Bengal (Bardhaman)": {"lat": 23.2324, "lon": 87.8615},
    "Madhya Pradesh (Indore)": {"lat": 22.7196, "lon": 75.8577},
    "Andhra Pradesh (Guntur)": {"lat": 16.3067, "lon": 80.4365}
}

def fetch_live_weather(location_name):
    """
    Fetches real-time environmental data (Temperature, Relative Humidity, 
    Precipitation, Wind Speed) using the free Open-Meteo REST API.
    No API key required.
    """
    coords = CITIES_GEO.get(location_name, {"lat": 28.6139, "lon": 77.2090})
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coords['lat']}&longitude={coords['lon']}&"
        f"current=temperature_2m,relative_humidity_2m,precipitation,surface_pressure,wind_speed_10m&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
        f"timezone=auto"
    )
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AgroSmartApp/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            current = data.get("current", {})
            daily = data.get("daily", {})
            return {
                "success": True,
                "temp": current.get("temperature_2m", 26.0),
                "humidity": current.get("relative_humidity_2m", 65.0),
                "precipitation": current.get("precipitation", 0.0),
                "wind_speed": current.get("wind_speed_10m", 5.0),
                "daily_rain_forecast": daily.get("precipitation_sum", [0.0] * 7),
                "daily_dates": daily.get("time", [])
            }
    except Exception as e:
        # Fallback graceful simulation if offline
        return {
            "success": False,
            "error": str(e),
            "temp": 27.5,
            "humidity": 62.0,
            "precipitation": 0.0,
            "wind_speed": 4.5,
            "daily_rain_forecast": [0.0, 2.1, 0.0, 5.4, 0.0, 0.0, 0.0],
            "daily_dates": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        }

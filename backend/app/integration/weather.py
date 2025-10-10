import requests
from datetime import date, datetime
import os
from ...models import WeatherResponse
from ...crud import create_or_update_weather
from ...database import get_db
from sqlalchemy.orm import Session

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_owm_key")

def fetch_weather(site_lat: float, site_lon: float, target_date: date, site_id: int, db: Session = None) -> list[WeatherResponse]:
    """
    Fetch weather data for a site/date from OpenWeatherMap (historical via timemachine).
    Interpolates to 96 blocks. Stores in DB if session provided.
    """
    timestamp = int(datetime(target_date.year, target_date.month, target_date.day).timestamp())
    url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={site_lat}&lon={site_lon}&dt={timestamp}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            # Assume hourly data; interpolate to 15-min (simplified: repeat per block)
            irradiance = current.get('uvi', 0) * 100  # UVI to rough W/m²
            temp = current.get('temp', 25.0)
            wind_speed = current.get('wind_speed', 5.0)
            cloud_cover = current.get('clouds', 50)
            
            blocks = []
            for block_no in range(1, 97):
                create_or_update_weather(db, site_id, target_date, block_no, irradiance, temp, wind_speed, cloud_cover) if db else None
                blocks.append(WeatherResponse(irradiance=irradiance, temp=temp, wind_speed=wind_speed, cloud_cover=cloud_cover))
            return blocks
        else:
            # Fallback mock
            return [WeatherResponse(irradiance=500.0, temp=25.0, wind_speed=5.0, cloud_cover=50) for _ in range(96)]
    except Exception as e:
        print(f"Weather API error: {e}")
        # Fallback
        return [WeatherResponse(irradiance=0, temp=0, wind_speed=0, cloud_cover=0) for _ in range(96)]

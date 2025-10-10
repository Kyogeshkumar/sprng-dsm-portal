from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from ...database import get_db
from ...crud import get_weather
from ...models import WeatherResponse
from ...auth import get_current_user
from ...integrations.weather import fetch_weather
from ...crud import get_site  # For lat/lon

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/{site_id}/{target_date}", response_model=list[WeatherResponse])
def get_weather_data(site_id: int, target_date: date, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get weather for site/date (auto-fetches from OpenWeather if missing).
    """
    site = get_site(db, site_id)
    if not site or not site.latitude or not site.longitude:
        raise HTTPException(400, "Site location (lat/lon) required for weather fetch")
    
    fetch_weather(site.latitude, site.longitude, target_date, site_id, db)  # Populate if needed
    weather_blocks = get_weather(db, site_id, target_date)
    return [WeatherResponse(irradiance=w.irradiance, temp=w.temp, wind_speed=w.wind_speed, cloud_cover=w.cloud_cover) for w in weather_blocks]

@router.get("/forecast/{site_id}/{target_date}")
def get_weather_forecast(site_id: int, target_date: date, db: Session = Depends(get_db)):
    """
    Simple forecast (use OpenWeather forecast endpoint; mock here).
    """
    # Similar to get_weather but for future date (API supports up to 5 days)
    site = get_site(db, site_id)
    if not site:
        raise HTTPException(404, "Site not found")
    # Mock forecast
    return {"forecast": "Sunny, Irradiance 600 W/m², Temp 28°C (mock; integrate full forecast API)"}

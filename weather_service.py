"""
weather_service.py - Giao tiếp với API thời tiết bên ngoài
===========================================================
Mục tiêu: Đóng gói toàn bộ việc gọi và chuẩn hóa dữ liệu từ Visual Crossing API.
"""

import requests
from config import CW_API

BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"


def fetch_weather_from_api(city: str) -> dict:
    """
    Gọi Visual Crossing API để lấy thời tiết mới nhất của thành phố.
    
    Có thể bắn ra các ngoại lệ (Exceptions):
      - requests.exceptions.HTTPError: Khi API báo lỗi 400/404/401...
      - requests.exceptions.ConnectionError: Mất mạng hoặc API sập
      - requests.exceptions.Timeout: API phản hồi quá chậm
    """
    url = (
        f"{BASE_URL}/{city.strip()}"
        f"?unitGroup=metric"
        f"&key={CW_API}"
        f"&contentType=json"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data.get("currentConditions", {})
    return {
        "city": data.get("resolvedAddress", city),
        "temperature": current.get("temp"),
        "feels_like": current.get("feelslike"),
        "humidity": current.get("humidity"),
        "description": current.get("conditions"),
        "wind_speed": current.get("windspeed"),
        "source": "Visual Crossing API (Fresh) 🌐"
    }


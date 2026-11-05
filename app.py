"""
app.py - API Gateway & Router chính
====================================
Mục tiêu: Đóng vai trò là controller/router tiếp nhận HTTP request từ Client,
điều phối giữa cache_service và weather_service, sau đó trả về JSON response.
"""

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests

from config import CW_API, APP_PORT, REDIS_HOST, REDIS_PORT
from cache_service import get_cached_weather, set_cached_weather, is_redis_available
from weather_service import fetch_weather_from_api

# ===== KHỞI TẠO FLASK APP & LIMITER =====
app = Flask(__name__)

# Giới hạn số lượt gọi API (Rate Limiting)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["30 per minute"],
    storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}"
)


# ===== ROUTES =====
@app.route("/")
def home():
    """Trang chủ hiển thị hướng dẫn sử dụng API."""
    return jsonify({
        "message": "Welcome to Weather API with Redis Caching! 🌦️⚡",
        "endpoints": {
            "get_weather": "/weather?city=<city_name>",
            "health_check": "/health"
        },
        "example": f"http://localhost:{APP_PORT}/weather?city=Hanoi"
    })


@app.route("/health")
def health():
    """Kiểm tra tình trạng sức khỏe của server và Redis."""
    redis_status = "connected ✅" if is_redis_available() else "disconnected ❌"
    return jsonify({
        "status": "healthy",
        "redis": redis_status
    })


@app.route("/weather")
@limiter.limit("5 per minute")
def get_weather():
    """Lấy thông tin thời tiết theo thành phố (áp dụng Cache-Aside)."""
    # 1. Kiểm tra tham số đầu vào
    city = request.args.get("city")
    if not city or not city.strip():
        return jsonify({
            "error": "Missing 'city' parameter",
            "usage": f"GET /weather?city=Hanoi"
        }), 400

    # 2. Kiểm tra Cache (Cache HIT)
    cached_data = get_cached_weather(city)
    if cached_data:
        return jsonify(cached_data)

    # 3. Nếu Cache MISS -> Gọi API ngoài
    try:
        fresh_data = fetch_weather_from_api(city)

        # Lưu lại vào Cache cho các lần gọi sau
        set_cached_weather(city, fresh_data)

        return jsonify(fresh_data)

    # 4. Xử lý các tình huống lỗi từ API ngoài
    except requests.exceptions.HTTPError:
        return jsonify({
            "error": f"Could not find weather data for '{city}'",
            "hint": "Check the city name or API key"
        }), 404

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Cannot connect to external weather service",
            "hint": "Check internet connection"
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Weather service is taking too long to respond"
        }), 504

    except Exception as e:
        return jsonify({
            "error": "An unexpected error occurred",
            "detail": str(e)
        }), 500


# ===== KHỞI CHẠY SERVER =====
if __name__ == "__main__":
    if not CW_API:
        print("⚠️ CẢNH BÁO: Chưa tìm thấy CW_API trong .env")
    else:
        print(f"✅ Đã tải API key: {CW_API[:4]}...")

    if is_redis_available():
        print(f"✅ Kết nối Redis Server ({REDIS_HOST}:{REDIS_PORT}) thành công!")
    else:
        print(f"⚠️ Không thể kết nối Redis Server. Hãy chắc chắn Redis đang chạy!")

    print(f"\n🌦️ Server đang chạy tại: http://localhost:{APP_PORT}")
    print(f"📍 Thử thời tiết: http://localhost:{APP_PORT}/weather?city=Hanoi\n")

    app.run(debug=True, port=APP_PORT)

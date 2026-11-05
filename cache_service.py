"""
cache_service.py - Xử lý tầng Cache với Redis
=============================================
Mục tiêu: Đóng gói toàn bộ logic liên quan đến Redis:
  - Kết nối Redis
  - Chuẩn hóa Key
  - Đọc cache (get) và chuyển từ JSON sang Dict
  - Ghi cache (set) kèm thời gian sống (TTL)
"""

import json
import redis
from config import REDIS_HOST, REDIS_PORT, CACHE_TTL

# Khởi tạo kết nối Redis
# decode_responses=True để tự động decode bytes thành string
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


def _make_key(city: str) -> str:
    """Hàm nội bộ: Chuẩn hóa tên thành phố thành key nhất quán trong Redis."""
    return f"weather:{city.strip().lower()}"


def get_cached_weather(city: str):
    """
    Tìm dữ liệu thời tiết của thành phố trong Redis.
    Trả về:
      - dict dữ liệu thời tiết (kèm source = 'cache') nếu tìm thấy.
      - None nếu không tìm thấy hoặc Redis gặp lỗi.
    """
    key = _make_key(city)
    try:
        cached_raw = redis_client.get(key)
        if cached_raw:
            data = json.loads(cached_raw)
            data["source"] = "cache (Redis) ⚡"
            return data
    except redis.RedisError as e:
        print(f"⚠️ Lỗi đọc Cache từ Redis: {e}")
    return None


def set_cached_weather(city: str, data: dict, ttl: int = CACHE_TTL) -> bool:
    """
    Lưu dữ liệu thời tiết vào Redis kèm thời gian hết hạn (TTL).
    Trả về True nếu thành công, False nếu lỗi.
    """
    key = _make_key(city)
    try:
        redis_client.set(key, json.dumps(data), ex=ttl)
        return True
    except redis.RedisError as e:
        print(f"⚠️ Lỗi ghi Cache vào Redis: {e}")
        return False


def is_redis_available() -> bool:
    """Kiểm tra Redis server có đang sống không."""
    try:
        return redis_client.ping()
    except (redis.ConnectionError, redis.RedisError):
        return False


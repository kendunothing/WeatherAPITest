"""
config.py - Quản lý cấu hình hệ thống
======================================
Mục tiêu: Đọc biến môi trường từ file .env một nơi duy nhất.
Các file khác chỉ cần `from config import CW_API, CACHE_TTL...`
"""

import os
from dotenv import load_dotenv

# Tải file .env
load_dotenv()

# API Key cho Visual Crossing
CW_API = os.getenv("CW_API")

# Cấu hình Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Thời gian sống của cache (mặc định 12 tiếng = 43200s)
CACHE_TTL = int(os.getenv("CACHE_TTL", 12 * 60 * 60))

# Cổng chạy ứng dụng Flask
APP_PORT = int(os.getenv("APP_PORT", 5002))


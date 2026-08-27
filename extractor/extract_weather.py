import os
import requests
import psycopg
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

# Danh sách thành phố cần lấy dữ liệu
CITIES = ["Hanoi", "Ho Chi Minh City", "Da Nang"]


def fetch_weather(city: str) -> dict:
    """Gọi API OpenWeatherMap để lấy dữ liệu thời tiết hiện tại của 1 thành phố."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()  # báo lỗi nếu API trả về status lỗi (401, 404...)
    return response.json()


def ensure_table_exists(conn):
    """Tạo bảng raw.weather_data nếu chưa tồn tại."""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.weather_data (
                id SERIAL PRIMARY KEY,
                city TEXT NOT NULL,
                fetched_at TIMESTAMPTZ NOT NULL,
                raw_json JSONB NOT NULL
            );
        """)
    conn.commit()


def save_weather(conn, city: str, data: dict):
    """Lưu dữ liệu raw JSON vào Postgres."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw.weather_data (city, fetched_at, raw_json)
            VALUES (%s, %s, %s)
            """,
            (city, datetime.now(timezone.utc), psycopg.types.json.Json(data)),
        )
    conn.commit()


def main():
    print("Bắt đầu lấy dữ liệu thời tiết...")
    conn = psycopg.connect(**DB_CONFIG)
    ensure_table_exists(conn)

    for city in CITIES:
        try:
            data = fetch_weather(city)
            save_weather(conn, city, data)
            print(f"✅ Đã lưu dữ liệu cho: {city}")
        except Exception as e:
            print(f"❌ Lỗi khi lấy dữ liệu cho {city}: {e}")

    conn.close()
    print("Hoàn tất.")


if __name__ == "__main__":
    main()
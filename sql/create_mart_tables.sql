-- Tạo schema và các bảng mart (star schema)
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS mart.dim_city (
    city_id SERIAL PRIMARY KEY,
    city_name TEXT UNIQUE NOT NULL,
    latitude NUMERIC,
    longitude NUMERIC
);

CREATE TABLE IF NOT EXISTS mart.fact_weather (
    id SERIAL PRIMARY KEY,
    city_id INT REFERENCES mart.dim_city(city_id),
    measured_at TIMESTAMPTZ NOT NULL,
    temperature NUMERIC,
    humidity NUMERIC,
    pressure NUMERIC,
    wind_speed NUMERIC,
    weather_description TEXT,
    UNIQUE (city_id, measured_at)
);
-- Transform raw JSON -> mart.dim_city
INSERT INTO mart.dim_city (city_name, latitude, longitude)
SELECT DISTINCT
    raw_json->>'name' AS city_name,
    (raw_json->'coord'->>'lat')::NUMERIC AS latitude,
    (raw_json->'coord'->>'lon')::NUMERIC AS longitude
FROM raw.weather_data
ON CONFLICT (city_name) DO NOTHING;

-- Transform raw JSON -> mart.fact_weather
INSERT INTO mart.fact_weather (city_id, measured_at, temperature, humidity, pressure, wind_speed, weather_description)
SELECT
    dc.city_id,
    to_timestamp((r.raw_json->>'dt')::BIGINT) AS measured_at,
    (r.raw_json->'main'->>'temp')::NUMERIC AS temperature,
    (r.raw_json->'main'->>'humidity')::NUMERIC AS humidity,
    (r.raw_json->'main'->>'pressure')::NUMERIC AS pressure,
    (r.raw_json->'wind'->>'speed')::NUMERIC AS wind_speed,
    r.raw_json->'weather'->0->>'description' AS weather_description
FROM raw.weather_data r
JOIN mart.dim_city dc ON dc.city_name = r.raw_json->>'name'
ON CONFLICT (city_id, measured_at) DO NOTHING;
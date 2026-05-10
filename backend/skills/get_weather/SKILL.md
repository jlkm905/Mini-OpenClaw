---
name: get_weather
description: Get real-time weather information for a specified city.
---

# Skill: Get Weather

**Trigger:** User asks about weather, temperature, or forecast for any location.

**Inputs:**
- `location` (string): City name or coordinates.

**Outputs:**
- Current temperature, conditions, and humidity.

## Execution Steps

1. Use `fetch_url` to resolve `location` to coordinates via the Open-Meteo geocoding API:
   `https://geocoding-api.open-meteo.com/v1/search?name=<location>&count=1`

2. Extract `latitude` and `longitude` from the JSON response.

3. Use `fetch_url` to fetch current weather:
   `https://api.open-meteo.com/v1/forecast?latitude=<lat>&longitude=<lon>&current=temperature_2m,relative_humidity_2m,weathercode&temperature_unit=celsius`

4. Use `python_repl` to parse the response JSON and print a concise weather summary
   (location name, temperature in °C, humidity %, and a plain-English condition derived from `weathercode`).

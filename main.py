from fastapi import FastAPI
import requests

app = FastAPI()
transitland_api_key = "9LmEldNXzFA6Z0YnclJCOtZLALm77L7q"

# https://shiny-rotary-phone-gjw45j64799h95jg-8000.app.github.dev/stopsWithArrivals?lat=53.45355045&lon=-113.59592569403735&radius=2000&route_type=3

@app.get("/times")
async def get_stops_with_arrivals(lat: float, lon: float, radius: int, route_type: int):
    headers = {"apikey": transitland_api_key}

    # Fetch stops
    stops_res = requests.get(
        f'https://transit.land/api/v2/rest/stops?lat={lat}&lon={lon}&radius={radius}&route_type={route_type}', 
        headers=headers
    )

    try:
        stops_response = stops_res.json()
    except Exception:
        return {"error": "Failed to parse stops response"}

    if "stops" not in stops_response:
        return {"error": "Invalid stops response", "response": stops_response}

    combined_data = []

    for stop in stops_response["stops"]:
        if "geometry" not in stop or "coordinates" not in stop["geometry"] or "id" not in stop or "stop_name" not in stop or "onestop_id" not in stop:
            continue  # Skip invalid stop data

        stop_id = stop["onestop_id"]
        stop_name = stop["stop_name"]
        coordinates = stop["geometry"]["coordinates"]

        # Fetch departures for this stop
        depart_res = requests.get(f'https://transit.land/api/v2/rest/stops/{stop_id}/departures', headers=headers)

        try:
            depart_response = depart_res.json()
        except Exception:
            departures = []
        else:
            departures = []
            if "stops" in depart_response and depart_response["stops"]:
                first_stop = depart_response["stops"][0]
                if "departures" in first_stop and first_stop["departures"]:
                    for departure in first_stop["departures"]:
                        route_info = departure.get("trip", {}).get("route", {})
                        route_short_name = route_info.get("route_short_name", "Unknown Route")
                        route_long_name = route_info.get("route_long_name", "Unknown Route Name")
                        arrival_time = departure.get("arrival_time", "N/A")

                        departures.append({
                            "route_short_name": route_short_name,
                            "route_long_name": route_long_name,
                            "arrival_time": arrival_time
                        })

        # Group arrivals by route
        routes_data = {}
        for dep in departures:
            route_key = f"{dep['route_short_name']} - {dep['route_long_name']}"
            if route_key not in routes_data:
                routes_data[route_key] = []
            routes_data[route_key].append(dep["arrival_time"])

        # Convert routes_data into a list format
        routes_list = [{"route_short_name": key.split(" - ")[0], "route_long_name": key.split(" - ")[1], "arrival_times": times} for key, times in routes_data.items()]

        # Append stop data with arrival times per route
        combined_data.append({
            "id": stop_id,
            "name": stop_name,
            "coordinates": coordinates,
            "routes": routes_list
        })

    return {"stops": combined_data}

from fastapi import FastAPI
import requests

app = FastAPI()
transitland_api_key = "9LmEldNXzFA6Z0YnclJCOtZLALm77L7q"

@app.get("/combinedStops")
async def get_combined_stops(lat: float, lon: float, radius: int, route_type: int):
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

    # Ensure 'stops' key exists
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
            arrival_time = "N/A"
        else:
            if "stops" in depart_response and depart_response["stops"]:
                first_stop = depart_response["stops"][0]
                if "departures" in first_stop and first_stop["departures"]:
                    first_departure = first_stop["departures"][0]
                    arrival_time = first_departure.get("arrival_time", "N/A")
                else:
                    arrival_time = "N/A"
            else:
                arrival_time = "N/A"

        # Append stop data with first arrival time
        combined_data.append({
            "id": stop_id,
            "name": stop_name,
            "coordinates": coordinates,
            "first_arrival_time": arrival_time
        })

    return {"stops": combined_data}



@app.get("/routes")
async def getActualStops(lat, long,radius):
    headers = {"apikey": transitland_api_key}

    res = requests.get(f'https://transit.land/api/v2/rest/routes/?lat={lat}&lon={long}&radius={radius}&route_type={route_type}', headers=headers)
    response = res.json()
    return response

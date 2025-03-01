from typing import Union
from fastapi import FastAPI
import requests
from requests.auth import HTTPBasicAuth
app = FastAPI()
transitland_api_key = "9LmEldNXzFA6Z0YnclJCOtZLALm77L7q"

@app.get("/correctStops")
#https://shiny-rotary-phone-gjw45j64799h95jg-8000.app.github.dev/correctStops?lat=53.45797055&lon=-113.37121373587301&radius=2000&route_type=3

async def getActualStops(lat, lon, radius, route_type):
    headers:dict = {"apikey": f"{transitland_api_key}"}

    res = requests.get(f'https://transit.land/api/v2/rest/stops?lat={lat}&lon={lon}&radius={radius}&route_type={route_type}', headers=headers)
    response = res.json()

    filtered_response: {[]}
    '''for i in range(len(response["stops"])):
        coord = response["stops"][1]["geometry"]["coordinates"]
        id = response["stops"][1]["id"]
        stop_name = response["stops"][1]["stop_name"]

        temp = {id: {stop_name: coord}}
        filtered_response[1].append(temp)'''


    return response["stops"][1]["geometry"]["coordinates"]



#!/usr/bin/env python3
from config import api_key
from datetime import datetime, timedelta
import googlemaps
from sys import argv

gmaps = googlemaps.Client(key=api_key)

origin = argv[1]
destination = argv[2]
date = datetime.now()

if len(argv) > 3:
    date = datetime.strptime(argv[3], "%m/%d/%Y")


direc = gmaps.directions(origin, destination, mode="transit",
                         departure_time=date)

distance_meters = direc[0]['legs'][0]['distance']['value']
distance_miles = distance_meters // 1609.344

time_converted = timedelta(seconds=direc[0]['legs'][0]['duration']['value'])

try:
    price = direc[0]['fare']['value']
except KeyError:
    price = 0

print("Road Trip!")
print(f"Distance: {distance_miles}")
print(f"Time: {time_converted}")
if (price is not 0):
    print(f"Total Cost: {price}")

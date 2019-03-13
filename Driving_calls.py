#!/usr/bin/env python3
import googlemaps
from datetime import datetime, timedelta
from sys import argv

gmaps = googlemaps.Client(key='AIzaSyA1yCIeh_gMwOkv_7hfGeOOVt7E9qr5a1g')

origin = argv[1]
destination = argv[2]
date = datetime.now()

if len(argv) > 3:
    date = datetime.strptime(argv[3], "%m/%d/%Y")


direc = gmaps.directions(origin, destination, mode="driving",
                         departure_time=date)

distance_meters = direc[0]['legs'][0]['distance']['value']
distance_miles = distance_meters // 1609.344

time_converted = timedelta(seconds=direc[0]['legs'][0]['duration']['value'])

wt_cost = (8.21 * distance_miles) // 100
gas_cost = (11.05 * distance_miles) // 100

print("Road Trip!")
print(f"Distance: {distance_miles}")
print(f"Time: {time_converted}")
print(f"Total Costs driving: ${wt_cost + gas_cost} ($.19/mile)")
print(f"Total Costs renting: ${gas_cost} ($.11/mile)")

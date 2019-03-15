#!/usr/bin/env python3
from config import api_key
from datetime import datetime, timedelta
import googlemaps
from sys import argv

if __name__ == "__main__":

    # initializing with API key
    gmaps = googlemaps.Client(key=api_key)

    # Locations can be city names, addresses, and can even have typos
    origin = argv[1]
    destination = argv[2]

    # Default date set to today
    date = datetime.now()

    # If a date is given, the date is set. Use mm/dd/yyy format.
    # When front and back are connected, change code to
    # if (date is not None) or something similar, don't count args
    if len(argv) > 3:
        date = datetime.strptime(argv[3], "%m/%d/%Y")

    # Inital API call is made with given variables and returns a
    # wealth of information
    direc = gmaps.directions(origin, destination, mode="driving",
                             departure_time=date)

    # Distance between locations is pulled and converted to miles from meters
    distance_meters = direc[0]['legs'][0]['distance']['value']
    distance_miles = distance_meters // 1609.344

    # Travel time is pulled and converted to hours, minutes, and seconds
    time_converted = timedelta(seconds=direc[0]['legs'][0]['duration']['value'])

    # Wear & tear costs and gas costs are average prices in cents per mile as
    # given by AAA for the year of 2018
    wt_cost = (8.21 * distance_miles) // 100
    gas_cost = (11.05 * distance_miles) // 100

    print("Road Trip!")
    print(f"Distance: {distance_miles}")
    print(f"Time: {time_converted}")
    print(f"Total Costs driving: ${wt_cost + gas_cost} ($.19/mile)")
    print(f"Total Costs renting: ${gas_cost} ($.11/mile)")

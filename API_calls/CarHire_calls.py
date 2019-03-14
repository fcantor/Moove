#!/usr/bin/python3
'''
Script that opens a flight search API session
'''
import requests
from sys import argv
import pprint
from config import car_key


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    origin_city_code = argv[1]
    origin_airport_code = argv[2]
    pickup_date = argv[3]
    pickup_hour = argv[4]
    dropoff_date = argv[5]
    dropoff_hour = argv[6]
    currency = argv[7]
    start_api = "https://apidojo-kayak-v1.p.rapidapi.com/cars/create-session?"
    list = [start_api, "origincitycode=", origin_city_code, "&originairportcode=", origin_airport_code, "&pickupdate=", pickup_date,
            "&pickuphour=", pickup_hour, "&dropoffdate=", dropoff_date, "&dropoffhour=", dropoff_hour, "&currency=", currency]
    api_string = "".join(list)
    response = requests.get(api_string,
                            headers={
                                "X-RapidAPI-Key": car_key
                            }
                            )
    try:
        json = response.json()
    except:
        print("Not a valid JSON")
    else:
        pp.pprint(json)

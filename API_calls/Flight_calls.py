#!/usr/bin/python3
'''
Script that opens a flight search API session
'''
from config import flight_key
import json
import requests
from sys import argv
import pprint


if __name__ == "__main__":
    origin = argv[1]
    destination = argv[2]
    depart_date = argv[3]
    cabin = argv[4]
    currency = 'USD'
    adults = '1'
    bags = '0'
    start_api = "https://apidojo-kayak-v1.p.rapidapi.com/flights/create-session?"
    list = [start_api, "origin1=", origin, "&destination1=", destination, "&departdate1=",
            depart_date, "&cabin=", cabin, "&currency=", currency, "&adults=", adults, "&bags", bags]
    api_string = "".join(list)
    response = requests.get(api_string,
                            headers={
                                "X-RapidAPI-Key": "NhPckVP3HYmshVQm7eKHEZxsKkVcp1RXXo3jsnN0exwdh5asqk",
                                "Content-Type": "Application/Json"
                            }
                            )
data = json.loads(response.text)
key_dict = {}
for k, v in data.items():
    key_dict[k] = v
for k, v in key_dict.items():
    if k == 'airportSummary':
        airport_summary = v
    if k == 'cheapestPrice':
        cheapest_price = v
    if k == 'departDate':
        depart_date = v
    if k == 'tripset':
        tripset = v
        for info in tripset:
            for a, b in info.items():
                if a == 'cheapestProviderName':
                    provider = b
                if a == 'duration':
                    duration = b
                if a == 'cabinClass':
                    cabin_class = b

print("The cheapest price from {} on {} is ${}".format(
    airport_summary, depart_date, cheapest_price))
print("Airline: {}".format(provider))
print("Duration: {}".format(duration))
print("Cabin Class: {}".format(cabin_class))

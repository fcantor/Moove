#!/usr/bin/python3
'''
Script that opens a flight search API session
'''
from config import flight_key
import json
import requests
from sys import argv



if __name__ == "__main__":
    # these are the necessary variables needed to make the api call
    origin = argv[1]
    destination = argv[2]
    depart_date = argv[3]
    cabin = argv[4]
    currency = 'USD'
    adults = '1'
    bags = '0'

    # beginning of link for api call
    start_api = "https://apidojo-kayak-v1.p.rapidapi.com/flights/create-session?"

    # concatenating variables to create the whole link needed to make the api call
    list = [start_api, "origin1=", origin, "&destination1=", destination, "&departdate1=", depart_date, "&cabin=", cabin, "&currency=", currency, "&adults=", adults, "&bags", bags]
    api_string = "".join(list)

    # api call; values received is stored in response variable
    response = requests.get(api_string,
    headers={
        "X-RapidAPI-Key": "NhPckVP3HYmshVQm7eKHEZxsKkVcp1RXXo3jsnN0exwdh5asqk",
        "Content-Type": "Application/Json"
        }
    )

    # jsonifying the values we received from the api call
    data = json.loads(response.text)

    # looping through the data to pull the values we need
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
            tripset = {}
            tripset = v
            flight = tripset[0]
    # these values shouldn't be in the for-loop as there are multiple values with the same name
    # and will override the first values, which we need
    airline = flight['cheapestProviderName']
    duration = flight['duration']
    cabin_class = flight['cabinClass']

    # printing out the variables to check whether we got the right values
    print("The cheapest price from {} on {} is ${}".format(airport_summary, depart_date, cheapest_price))
    print("Airline: {}".format(airline))
    print("Duration: {} minutes".format(duration))
    print("Cabin Class: {}".format(cabin_class))
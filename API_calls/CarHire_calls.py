#!/usr/bin/env python3
'''
Script that opens a car hire search API session
'''
import csv
import json
import pprint
import requests
from config import car_key
from sys import argv

pp = pprint.PrettyPrinter(indent=4)

def findCity(origin_city):
    ''' This method takes in a city code and returns the name of the city in plain text '''
    # open csv file
    with open('city-codes.csv') as csv_file:
        # read through file
        csv_reader = csv.reader(csv_file, delimiter=',')
        # iterate through file until city_id is found
        for row in csv_reader:
            if row[1] == origin_city:
                # return plain text city
                return(row[0])


def createSession():
    ''' This method makes an API call and creates a session '''
    # first convert City, State to city_id for API call
    origin_city_code = findCity(argv[1])

    # if that was successful, create the session
    if origin_city_code is not None:
        origin_airport_code = argv[2]
        pickup_date = '2019-03-21'
        pickup_hour = '8'
        dropoff_date = '2019-03-21'
        dropoff_hour = '22'
        currency = 'USD'
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
            return (json['searchid'])
    else:
        print("Please enter proper 'City, State'")


def pollSession(session_id):
    ''' This polls the data from the session opened by createSession method '''
    api_start = "https://apidojo-kayak-v1.p.rapidapi.com/cars/poll?searchid="
    api_end = "&currency=USD"
    list = [api_start, session_id, api_end]
    api_string = "".join(list)
    response = requests.get(api_string,
        headers={
            "X-RapidAPI-Key": "NhPckVP3HYmshVQm7eKHEZxsKkVcp1RXXo3jsnN0exwdh5asqk"
            }
    )

    # jsonifying the values we received from the api call
    data = json.loads(response.text)

    # API is not always reliable and will sometimes fail; this is a test to see if we can pull values
    try:
        test_value = data['carset']
    except KeyError:
        print("System error. Please try your request again.")
    
    # if we were able to successfully pull values into test_value variable, then continue ahead
    if test_value:
        pickup_location = data['carset'][0]['agency']['pickupLocation']['city']
        dropoff_location = data['carset'][0]['agency']['dropoffLocation']['city']
        rental_place = data['carset'][0]['cheapestProviderName']
        origin_city = argv[1]
        rental_car = data['carset'][0]['car']['brand']
        price = data['carset'][0]['displayFullPrice']

        # printing the variables above
        print("Cheapest car rental from {} is in {}".format(origin_city, pickup_location))
        print("Car Rental Agency: {}".format(rental_place))
        print("Car: {}".format(rental_car))
        print("Price: {}".format(price))
        print("Please drop off the car at: {}".format(dropoff_location))
    else:
        print("System error. Please try your request again.")


if __name__ == "__main__":
    session_id = createSession()
    pollSession(session_id)


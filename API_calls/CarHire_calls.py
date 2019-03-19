#!/usr/bin/env python3
'''
Script that opens a car hire search API session
'''
from config import api_key, car_key
from datetime import datetime
import googlemaps
import csv
import json
import pprint
import re
import requests
from sys import argv

pp = pprint.PrettyPrinter(indent=4)

# initializing with API key
gmaps = googlemaps.Client(key=api_key)

# Geocoding call is made to find the closest city to the user inputted string
# and then results are parsed to pull city name and state/country name
all_states = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}
full_address = gmaps.geocode(address=argv[1])[0]["formatted_address"]
address_list = [i.strip() for i in full_address.split(",")]
origin_city_and_state = address_list[0]
destination = argv[2]
if address_list[2] == "USA":
    origin_city_and_state += (", " + all_states[address_list[1]])
else:
    origin_city_and_state += (", " + address_list[2])


def findCity(origin_city_and_state):
    ''' This method takes in a city code and returns the name
        of the city in plain text '''
    # open csv file
    with open('city-codes.csv') as csv_file:
        # read through file
        csv_reader = csv.reader(csv_file, delimiter=',')
        # iterate through file until city_id is found
        for row in csv_reader:
            if row[1] == origin_city_and_state:
                # return plain text city
                return(row[0])
                print(row[1])


def createSession():
    ''' This method makes an API call and creates a session '''
    # first convert City, State to city_id for API call
    origin_city_code = findCity(origin_city_and_state)
    # if that was successful, create the session
    if origin_city_code is not None:
        origin_res = gmaps.geocode(address="airport " + argv[1])[0]["formatted_address"]
        origin_airport_code = re.search(r'\((.*?)\)', origin_res).group(1)
        # Default date is today
        pickup_date = datetime.now().strftime("%Y-%m-%d")
        # If a date is given, the date is set. Use mm/dd/yyy format.
        # When front and back are connected, change code to
        # if (date is not None) or something similar, don't count args
        if len(argv) > 3:
            pickup_date = datetime.strptime(argv[3], "%m/%d/%Y").strftime("%Y-%m-%d")
        pickup_hour = '8'
        # Default date is today
        dropoff_date = pickup_date

        # If a date is given, the date is set. Use mm/dd/yyy format.
        # leaving this included for when we expand to multiday trips
        # if len(argv) > 4:
        #     dropoff_date = datetime.strptime(argv[4], "%m/%d/%Y").strftime("%Y-%m-%d")

        dropoff_hour = '22'
        currency = 'USD'
        start_api = "https://apidojo-kayak-v1.p.rapidapi.com/cars/create-session?"
        list = [start_api, "origincitycode=", origin_city_code,
                "&originairportcode=", origin_airport_code, "&pickupdate=",
                pickup_date, "&pickuphour=", pickup_hour, "&dropoffdate=",
                dropoff_date, "&dropoffhour=", dropoff_hour, "&currency=",
                currency]
        api_string = "".join(list)
        response = requests.get(api_string, headers={"X-RapidAPI-Key": car_key})
        try:
            json = response.json()
        except:
            print("Not a valid JSON")
        else:
            try:
                return (json['searchid'])
            except KeyError:
                print("No Cars for this date")
    else:
        print("Please enter proper 'City, State'")


# Google maps directions to get miles to destination
direc = gmaps.directions(origin_city_and_state, destination, mode="driving",
                         departure_time=datetime.strptime(argv[3], "%m/%d/%Y"))
distance_meters = direc[0]['legs'][0]['distance']['value']
distance_miles = distance_meters // 1609.344
gas_cost = (11.05 * distance_miles) // 100


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

    # API is not always reliable and will sometimes fail; this is a test
    # to see if we can pull values
    test_value = []
    try:
        test_value = data['carset']
    except KeyError:
        print("System error. Please try your request again.")

    # if we were able to successfully pull values into test_value variable,
    # then continue ahead
    if test_value:
        pickup_location = data['carset'][0]['agency']['pickupLocation']['city']
        dropoff_location = data['carset'][0]['agency']['dropoffLocation']['city']
        rental_place = data['carset'][0]['cheapestProviderName']
        origin_city_and_state = argv[1]
        rental_car = data['carset'][0]['car']['brand']
        price = int(data['carset'][0]['displayFullPrice'][1:])

        # printing the variables above
        print("Cheapest car rental from {} to {} is in {}".format(origin_city_and_state,
                                                                  destination,
                                                                  pickup_location))
        print("Car Rental Agency: {}".format(rental_place))
        print("Car: {}".format(rental_car))
        print("Rental Price: ${}".format(price))
        print("Total Price (including gas): ${}".format(gas_cost + price))
        print("Please drop off the car at: {}".format(dropoff_location))
    else:
        print("System error. Please try your request again.")


if __name__ == "__main__":
    session_id = createSession()
    pollSession(session_id)

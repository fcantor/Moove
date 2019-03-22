#!/usr/bin/env python3
"""
Flask app that integrates with static HTML template
"""
from config import api_key, flight_key, car_key
import csv
from datetime import datetime
from flask import Flask, request, render_template, make_response, jsonify
from flask_cors import CORS, cross_origin
import googlemaps
import json
import re
import requests
from sys import argv
from os import getenv, system
from filestorage import save, deserialize

# flask setup
app = Flask(__name__)

# global strict slashes
app.url_map.strict_slashes = False

# flask server environmental setup
host = getenv('API_HOST', '0.0.0.0')
port = getenv('API_PORT', 5001)

# Cross-Origin Resource Sharing
cors = CORS(app, resources={r"/web_dynamic/*": {"origins": "*"}})

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

@app.route('/')
def index():
    """
    Function that returns the index page
    """
    return render_template("index.html")

@app.route('/results', methods=['POST', 'GET'])
def resultsWithData():
    """
    Takes data backend and sends to front end
    """
    if request.method == 'POST':
        origin = request.json['origin'];
        destination = request.json['destination'];
        date = request.json['selectedDate'];
        print("\n\nHERE!!!\n\n{} {} {}".format(origin, destination, date))

        # get flight data
        flightDict = {}
        flightDict = flightFunc(origin, destination, date)

        # get car rental data
        session_id = createSession(origin, destination, date)
        print("THIS IS THE SESSION ID!!! {}".format(session_id))
        rentalDict = pollSession(session_id, origin, destination, date)

        allResults = {}
        allResults = {
            'flight': flightDict,
            'rental': rentalDict
        }
        print("ALL RESULTS!!!! {}".format(allResults))
        save(allResults)
        return render_template("results.html")
    else:
        print("THIS IS A GET METHOD")
        results = deserialize()
        print(results)
        return render_template("results.html", results=results)

@app.route('/loading')
def loading():
    """
    Function that returns the flight page
    """
    return render_template("loading.html")

@app.errorhandler(404)
def handle_404(exception):
    """
    Handles 404 errors, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    message = {'error': description}
    return make_response(jsonify(message), code)

@app.errorhandler(400)
def handle_400(exception):
    """
    handles 400 errros, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    message = {'error': description}
    return make_response(jsonify(message), code)

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

# DRIVING

# initializing with API key
def getCarData(origin, destination, date):
    gmaps = googlemaps.Client(key=api_key)

    # Default date set to today
    date = datetime.now()

    # # If a date is given, the date is set. Use mm/dd/yyy format.
    # # When front and back are connected, change code to
    # # if (date is not None) or something similar, don't count args
    # if len(argv) > 3:
    #     date = datetime.strptime(argv[3], "%m/%d/%Y")

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
    total_cost = wt_cost + gas_cost

    print("Road Trip!")
    print(f"Distance: {distance_miles}")
    print(f"Time: {time_converted}")
    print(f"Total Costs driving: ${wt_cost + gas_cost} ($.19/mile)")
    print(f"Total Costs renting: ${gas_cost} ($.11/mile)")

    carDict = {}
    carDict = {
        'distance_miles': distance_miles,
        'time_converted': time_converted,
        'total_cost': total_cost,
        'gas_cost': gas_cost
    }
    return (carDict)


# CAR RENTAL

def findCity(origin_city_and_state):
    ''' This method takes in a city code and returns the name
        of the city in plain text '''
    try:
        with open('city-codes.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                print("ROW!!!! {}".format(row))
                if row[1] == origin_city_and_state:
                    return(row[0])
                    print("THIS IS ROW 1: {}".format(row[1]))
    except FileNotFoundError:
        return ('79830')


def createSession(origin, destination, date):
    ''' This method makes an API call and creates a session '''
    full_address = gmaps.geocode(address=origin)[0]["formatted_address"]
    address_list = [i.strip() for i in full_address.split(",")]
    origin_city_and_state = address_list[0]
    if address_list[2] == "USA":
        origin_city_and_state += (", " + all_states[address_list[1]])
    else:
        origin_city_and_state += (", " + address_list[2])
    # first convert City, State to city_id for API call
    origin_city_code = findCity(origin_city_and_state)
    # if that was successful, create the session
    print("ORIGIN CITY CODE {}".format(origin_city_code))
    if origin_city_code is not None:
        origin_res = gmaps.geocode(address="airport " + origin)[0]["formatted_address"]
        origin_airport_code = re.search(r'\((.*?)\)', origin_res).group(1)
        # Default date is today
        pickup_date = datetime.now().strftime("%Y-%m-%d")
        # If a date is given, the date is set. Use mm/dd/yyy format.
        # When front and back are connected, change code to
        # if (date is not None) or something similar, don't count args
        if date is not None:
            pickup_date = date #datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
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
        json = response.json()
        try:
            print("\nI'M IN POLL SESSION!!!\n")
            return (json['searchid'])
        except KeyError:
            print("No cars for this date.\nPlease try another date!")
    else:
        print("Please enter proper 'City, State'")

def getMileage(origin_city_and_state, destination, date):
    # Google maps directions to get miles to destination
    direc = gmaps.directions(origin_city_and_state, destination, mode="driving",
                            departure_time=datetime.strptime(date, "%Y-%m-%d"))
    distance_meters = direc[0]['legs'][0]['distance']['value']
    distance_miles = distance_meters // 1609.344
    gas_cost = (11.05 * distance_miles) // 100
    print("I'M IN GETMILEAGE!")
    return (gas_cost)


def pollSession(session_id, origin, destination, date):
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
        origin_city_and_state = origin
        rental_car = data['carset'][0]['car']['brand']
        price = int(data['carset'][0]['displayFullPrice'][1:])
        gas_cost = getMileage(origin_city_and_state, destination, date);
        carRentalDict = {}
        carRentalDict = {
            'rental_pickup': pickup_location,
            'rental_dropoff': dropoff_location,
            'rental_provider': rental_place,
            'rental_origin': origin_city_and_state,
            'rental_car': rental_car,
            'rental_price': price,
            'rental_gas': gas_cost
        }
        print("\n\n\I'M IN CARRENTAL!! {}\n\n".format(carRentalDict))
        return (carRentalDict)
        # printing the variables above
        # print("Cheapest car rental from {} to {} is in {}".format(origin_city_and_state,
        #                                                         destination,
        #                                                         pickup_location))
        # print("Car Rental Agency: {}".format(rental_place))
        # print("Car: {}".format(rental_car))
        # print("Rental Price: ${}".format(price))
        # print("Total Price (including gas): ${}".format(gas_cost + price))
        # print("Please drop off the car at: {}".format(dropoff_location))
    else:
        print("System error. Please try your request again.")



# FLIGHT
# class Flights(origin, destination, date):
def notAirline(tripset):
    ''' This function finds the value in tripset that isn't a listed airline '''
    # list of airlines available in the API
    airlines = ['Boutique Air', 'Major Airline', 'American Airlines',
                'Alaska Airlines', 'JetBlue', 'Delta', 'Frontier',
                'Hawaiian Airlines', 'Multiple Airlines', 'Spirit Airlines',
                'Linear Air Taxi', 'United Airlines', 'Southwest', 'JetSuiteX']
    x = 0

    # loop through all the data in tripset, which is a set of details per flight
    for detail in tripset:
        # if the cheapest provider name is not in the airlines list above
        if tripset[x]['cheapestProviderName'] not in airlines:
            # move onto the next set until you get a set that includes an
            # airline listed in the airlines list above
            x = x + 1
    return(tripset[x])

def flightFunc(origin, destination, date):
    """
    API endpoint that gets information from routes endpoint
    """
    print("IN FLIGHTFUNC!!!!\n\n{}\n\n".format(origin))
    if origin and destination and date:
        # these are the necessary variables needed to make the api call
        cabin = 'e'
        depart_date = datetime.now().strftime("%Y-%m-%d")
        currency = 'USD'
        adults = '1'
        bags = '0'

        # Geocoding API call is made and results are parsed to get airport code
        # for origin and destination
        origin_res = gmaps.geocode(address="airport " + origin)[0]["formatted_address"]
        origin_code = re.search(r'\((.*?)\)', origin_res).group(1)
        destination_res = gmaps.geocode(address="airport " + destination)[0]["formatted_address"]
        destination_code = re.search(r'\((.*?)\)', destination_res).group(1)

        # If a date is given, the date is set. Use mm/dd/yyy format.
        # When front and back are connected, change code to
        # if (date is not None) or something similar, don't count args
        if date is not None:
            depart_date = date #datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")

        # beginning of link for api call
        start_api = "https://apidojo-kayak-v1.p.rapidapi.com/flights/create-session?"

        # concatenating variables to create the whole link needed to make the api call
        list = [start_api, "origin1=", origin_code, "&destination1=",
                destination_code, "&departdate1=", depart_date, "&cabin=",
                cabin, "&currency=", currency, "&adults=", adults, "&bags", bags]
        api_string = "".join(list)

        # api call; values received is stored in response variable
        response = requests.get(api_string,
                                headers={
                                    "X-RapidAPI-Key": "NhPckVP3HYmshVQm7eKHEZxsKkVcp1RXXo3jsnN0exwdh5asqk",
                                    "Content-Type": "Application/Json"
                                })

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
                tripset = []  # turn object into dictionary
                tripset = v

        flight = notAirline(tripset)
        # these values shouldn't be in the for-loop as there are multiple
        # values with the same name and will override the first values, which we need
        airline = flight['cheapestProviderName']
        duration = flight['duration']
        try:
            cabin_class = flight['fareFamily']['displayName']
        except KeyError:
            cabin_class = 'Economy'

        # store the data in filestorage
        dict = {}
        dict = {'airline_summary': airport_summary,
                        'airline_depart': depart_date,
                        'airline_price': cheapest_price,
                        'airline': airline,
                        'airline_duration': duration,
                        'airline_cabin': cabin_class}
        return (dict)
        print("SUCCESS!")


if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
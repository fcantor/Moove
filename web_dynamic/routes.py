#!/usr/bin/env python3
"""
Flask app that integrates with static HTML template
"""
from config import api_key, flight_key
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

        # initializing with API key
        gmaps = googlemaps.Client(key=api_key)

        # Geocoding API call is made and results are parsed to get airport code
        # for origin and destination
        origin_res = gmaps.geocode(address="airport " + origin)[0]["formatted_address"]
        origin_code = re.search(r'\((.*?)\)', origin_res).group(1)
        destination_res = gmaps.geocode(address="airport " + destination)[0]["formatted_address"]
        destination_code = re.search(r'\((.*?)\)', destination_res).group(1)

        # If a date is given, the date is set. Use mm/dd/yyy format.
        # When front and back are connected, change code to
        # if (date is not None) or something similar, don't count args
        if len(argv) > 4:
            depart_date = datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")

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
        cabin_class = flight['fareFamily']['displayName']

        # store the data in filestorage
        dict = {}
        dict = {'airport_summary': airport_summary,
                        'depart_date': depart_date,
                        'cheapest_price': cheapest_price,
                        'airline': airline,
                        'duration': duration,
                        'cabin_class': cabin_class}
        save(dict)
        print("SUCCESS!")

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
        dict = flightFunc(origin, destination, date)
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

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
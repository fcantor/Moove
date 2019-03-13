#!/usr/bin/python3
'''
Script that opens a flight search API session
'''
import requests
from sys import argv
import pprint
from config import flight_key


if __name__ == "__main__":
  pp = pprint.PrettyPrinter(indent=4)
  origin = argv[1]
  destination = argv[2]
  depart_date = argv[3]
  cabin = argv[4]
  currency = argv[5]
  adults = argv[6]
  bags = argv[7]
  start_api = "https://apidojo-kayak-v1.p.rapidapi.com/flights/create-session?"
  list = [start_api, "origin1=", origin, "&destination1=", destination, "&departdate1=", depart_date, "&cabin=", cabin, "&currency=", currency, "&adults=", adults, "&bags", bags]
  api_string = "".join(list)  
  response = requests.get(api_string,
  headers={
    "X-RapidAPI-Key": flight_key
  }
)
  try:
    json = response.json()
  except:
    print("Not a valid JSON")
  else:
    pp.pprint(json)
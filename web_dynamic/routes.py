#!/usr/bin/env python3
"""
Flask app that integrates with static HTML template
"""
from flask import Flask, request, render_template, make_response, jsonify
from os import getenv, system

# flask setup
app = Flask(__name__)

# global strict slashes
app.url_map.strict_slashes = False

# flask server environmental setup
host = getenv('API_HOST', '0.0.0.0')
port = getenv('API_PORT', 5001)

@app.route('/')
def index():
    """
    Function that returns the index page
    """
    return render_template("index.html")

@app.route('/loading')
def loading():
    """
    Function that returns the flight page
    """
    return render_template("loading.html")

@app.route('/results/<origin>/<destination>/<date>', methods=['POST', 'GET'])
def results():
    """
    Function that returns the car-rental page
    """
    origin = request.json['origin']
    destination = request.json['destination']
    date = request.json['date']

    print("Origin: {}".format(origin))
    print("Destination: {}".format(destination))
    print("Date: {}".format(date))
    return render_template("results.html")

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
def handle_404(exception):
    """
    handles 400 errros, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    message = {'error': description}
    return make_response(jsonify(message), code)

if __name__ == '__main__':
    app.run(host=host, port=port)
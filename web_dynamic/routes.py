#!/usr/bin/env python3
"""
Flask app that integrates with static HTML template
"""
from flask import Flask, request, render_template, make_response, jsonify
from flask_cors import CORS, cross_origin
from os import getenv, system

# flask setup
app = Flask(__name__)

# global strict slashes
app.url_map.strict_slashes = False

# flask server environmental setup
host = getenv('API_HOST', '0.0.0.0')
port = getenv('API_PORT', 5001)

# Cross-Origin Resource Sharing
cors = CORS(app, resources={r"/web_dynamic/*": {"origins": "*"}})

@app.route('/')
def index():
    """
    Function that returns the index page
    """
    return render_template("index.html")

@app.route('/results')
def results():
    """
    Takes data backend and sends to front end
    """
    url = 'http://0.0.0.0:5000/flightResults'
    # data = {
    #     origin: request.data['origin'],
    #     destination: request.data['destination'],
    #     date: request.data['date']
    # }
    r = request.get_json()
    print("THIS IS R: {}".format(r))
    return render_template('results.html', data=r)

@app.route('/loading')
def loading():
    """
    Function that returns the flight page
    """
    return render_template("loading.html")

# @app.route('/results', methods=['POST', 'GET'])
# def results():
#     """
#     Function that returns takes in data from the front-end and passes it
#     back out to respective get requests
#     """
#     return render_template("results.html")

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
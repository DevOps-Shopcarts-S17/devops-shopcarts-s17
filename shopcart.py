# Copyright 2016, 2017 Hongtao Cheng. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
from threading import Lock
from flask import Flask, Response, jsonify, request, make_response, json, url_for

# Create Flask application
app = Flask(__name__)
app.config['LOGGING_LEVEL'] = logging.INFO

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# Data Store, pre-populated with sample data
######################################################################
shopping_carts = [
    {
        'uid':1,
        'sid':  1,
        'products': [
            {
                'sku': 123456780,
                'quantity': 2,
                'name': "Settlers of Catan",
                'unitprice': 27.99,
            },
            {
                'sku': 876543210,
                'quantity': 1,
                'name': "Risk",
                'unitprice': 27.99,
            }
        ]
    },
    {
        'uid':2,
        'sid':  2,
        'products': []
    },
    {
        'uid': 3,
        'sid': 3,
        'products': [
            {
                'sku': 011467250,
                'quantity': 1,
                'name': "Game of Life",
                'unitprice': 13.99,
            }
        ]
    },
]

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return make_response("Hello World", HTTP_200_OK)

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        handler = logging.StreamHandler()
        handler.setLevel(app.config['LOGGING_LEVEL'])
        # formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
        #'%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    # Pull options from environment
    debug = (os.getenv('DEBUG', 'False') == 'True')
    port = os.getenv('PORT', '8888')
    app.run(host='0.0.0.0', port=int(port), debug=debug)

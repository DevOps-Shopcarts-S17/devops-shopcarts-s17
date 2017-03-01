# Copyright 2016, 2017 Echo Squad. All Rights Reserved.
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

# Lock for thread-safe counter increment
lock = Lock()

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
                'unitprice': 27.99
            },
            {
                'sku': 876543210,
                'quantity': 1,
                'name': "Risk",
                'unitprice': 27.99
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
                'sku': 114672050,
                'quantity': 1,
                'name': "Game of Life",
                'unitprice': 13.99
            }
        ]
    },
]

current_shopping_cart_id = 4

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return make_response("Hello World", HTTP_200_OK)

######################################################################
# ADD A NEW SHOPPING CART
######################################################################
@app.route('/shopcarts', methods=['POST'])
def create_shopcarts():
    payload = request.get_json()
    if is_validShoppingCart(payload):
        id = next_sid()
        if 'products' not in payload:
            payload['products'] = []
        shopcart = {'uid': payload['uid'],'sid': id, 'products': payload['products']}
        shopping_carts.append(shopcart)
        message = shopcart
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST

    response = make_response(jsonify(message), rc)
    if rc == HTTP_201_CREATED:
        response.headers['Location'] = url_for('get_shopcart', sid=id)
    return response

######################################################################
# ADD A NEW PRODUCT IN A SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>/products', methods=['POST'])
def create_products(sid):
    cart = [cart for cart in shopping_carts if cart['sid']==sid]
    if len(cart) > 0:  
        payload = request.get_json()
        if is_validProduct(payload):
            for i in range(0,len(payload['products'])): 
                product = {'sku': payload['products'][i]['sku'],'quantity': payload['products'][i]['quantity'], 'name': payload['products'][i]['name'], 'unitprice' : payload['products'][i]['unitprice']}
                cart[0]['products'].append(product)
            message = cart[0]
            rc = HTTP_201_CREATED
        else:
            message = { 'error' : 'Data is not valid' }
            rc = HTTP_400_BAD_REQUEST

        response = make_response(jsonify(message), rc)
        if rc == HTTP_201_CREATED:
            response.headers['Location'] = url_for('get_product', sku = payload['sku'], sid=shopping_carts[cart[0].sid])
        return response
    else:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND
        return make_response(jsonify(message), rc)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def next_sid():
    global current_shopping_cart_id
    with lock:
        current_shopping_cart_id += 1
    return current_shopping_cart_id

def is_validProduct(data):
    valid = False
    try:
        for i in range(0,len(data['products'])):  
            sku = data['products'][i]['sku']
            quantity = data['products'][i]['quantity']
            name = data['products'][i]['name']
            unitprice = data['products'][i]['unitprice']
        valid = True
    except KeyError as err:
        app.logger.warn('Missing parameter error: %s', err)
    except TypeError as err:
        app.logger.warn('Invalid Content Type error: %s', err)

    return valid

def is_validShoppingCart(data):
    valid = False
    try:
        user_id = data['uid']
        valid = True
    except KeyError as err:
        app.logger.warn('Missing parameter error: %s', err)
    except TypeError as err:
        app.logger.warn('Invalid Content Type error: %s', err)

    return valid

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

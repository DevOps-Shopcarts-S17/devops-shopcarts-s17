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
                'sku': 114672050,
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
    shopcarts_url = request.base_url + "shopcarts"
    return make_response(jsonify(name='Shopcart Demo REST API Service',
                   version='1.0',
                   url=shopcarts_url
                   ), HTTP_200_OK)

######################################################################
# LIST ALL SHOPCARTS FOR ALL USERS
######################################################################
#USAGE: /shopcarts or /shopcarts?sid=1 for quering for a user
@app.route('/shopcarts', methods=['GET'])
def list_shopcarts():
    results=[]
    sid=request.args.get('sid')
    if sid:
        #Extra check for query input
        try:
            sid = int(sid)
        except ValueError:
            return make_response(jsonify(shopping_carts), HTTP_200_OK)

        results=[cart for cart in shopping_carts if cart['sid']==int(sid)]
        if len(results)==0:
            results=shopping_carts
        else:

            if len(results[0]['products'])==0:
                results='The cart contains no products'
            else:
                results=results[0]['products']
    else:
        results=shopping_carts

    return make_response(jsonify(results), HTTP_200_OK)

######################################################################
# RETRIEVE A USER'S CART
######################################################################
#USAGE: /shopcarts/3
@app.route('/shopcarts/<int:sid>', methods=['GET'])
def get_shopcart(sid):
    carts = [cart for cart in shopping_carts if cart['sid']==sid]
    if len(carts) > 0:
        message = carts[0]['products']
        if not message:
            message='The cart contains no products'
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND

    return make_response(jsonify(message), rc)

######################################################################
# RETRIEVE USER'S PRODUCTS LIST IN THE CART
######################################################################
#USAGE: /shopcarts/3/products or /shopcarts/3/products?sku=114672050 for querying for a product
@app.route('/shopcarts/<int:sid>/products', methods=['GET'])
def get_products(sid):
    carts = [cart for cart in shopping_carts if cart['sid']==sid]
    sku = request.args.get('sku')
    if len(carts) > 0:
        products = carts[0]['products']
        if(len(products)==0):
            message='The cart contains no products'
        else:
            if sku:
                #Extra check for query input
                try:
                    sku = int(sku)
                except ValueError:
                    return make_response(jsonify(products), HTTP_200_OK)

                message=[product for product in products if product['sku']==int(sku)]
                if len(message)==0:
                    message=products
                else:
                    message=message[0]
            else:
                message=products
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND

    return make_response(jsonify(message), rc)

######################################################################
# RETRIEVE A PRODUCT FROM USER'S SHOPCART
######################################################################
#USAGE: /shopcarts/3/products/114672050
@app.route('/shopcarts/<int:sid>/products/<int:sku>', methods=['GET'])
def get_product(sid,sku):
    carts = [cart for cart in shopping_carts if cart['sid']==sid]
    if(len(carts)==0):
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        return make_response(jsonify(message),HTTP_404_NOT_FOUND)
    else:
        products=[product for product in carts[0]['products'] if product['sku']==sku]
        if(len(products)==0):
            message = { 'error' : 'Product with sku: %s was not found in the cart for user %s' % (str(sku), str(sid))}
            return make_response(jsonify(message),HTTP_404_NOT_FOUND)
        else:
            return make_response(jsonify(products[0]), HTTP_200_OK)


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

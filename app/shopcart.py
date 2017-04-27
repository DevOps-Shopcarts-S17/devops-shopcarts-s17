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

import urllib
import os
import logging
from redis import Redis
from redis.exceptions import ConnectionError
from threading import Lock
from flask import Flask, Response, jsonify, request, make_response, json, url_for
from flasgger import Swagger
from models import Shopcart
from . import app
import error_handlers

# Create Flask application
app.config['LOGGING_LEVEL'] = logging.INFO

# Swagger set up
# Configure Swagger before initilaizing it
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "DevOps Swagger Shopcarts App",
            "description": "This is a Shopping cart API server.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

# Initialize Swagger after configuring it
Swagger(app)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

redis = None

# Lock for thread-safe counter increment
lock = Lock()

######################################################################
# Data Store, pre-populated with sample data
######################################################################
shopping_carts = []

current_shopping_cart_id = 3

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    shopcarts_url = request.base_url + 'shopcarts'
    return make_response(jsonify(name='Shopcart Demo REST API Service v1.0',
                   version='1.0',
                   url=shopcarts_url
                   ), HTTP_200_OK)

######################################################################
# LIST ALL SHOPCARTS FOR ALL USERS
######################################################################
# USAGE: /shopcarts or /shopcarts?uid=1 for quering for a user
@app.route('/shopcarts', methods=['GET'])
def list_shopcarts():
    results=[]
    uid=request.args.get('uid')
    if uid:
        #Extra check for query input
        try:
            uid = int(uid)
        except ValueError:
            message={ 'error' : 'Data is not valid' }
            return make_response(jsonify(message), HTTP_400_BAD_REQUEST)

        results=Shopcart.find_by_uid(uid)
        if len(results)!=0:
            results=results[0]
            rc=HTTP_200_OK
        else:
            results={ 'error' : 'Shopping Cart under user id: %s was not found' % str(uid) }
            rc=HTTP_404_NOT_FOUND
    else:
        results=Shopcart.all()
        rc=HTTP_200_OK

    return make_response(jsonify(results), rc)

######################################################################
# RETRIEVE A USER'S CART
######################################################################
# USAGE: /shopcarts/3
@app.route('/shopcarts/<int:sid>', methods=['GET'])
def get_shopcart(sid):
    carts = [cart for cart in shopping_carts if cart['sid']==sid]
    if len(carts) > 0:
        message = carts[0]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND

    return make_response(jsonify(message), rc)

######################################################################
# RETRIEVE USER'S PRODUCTS LIST IN THE CART
######################################################################
# USAGE: /shopcarts/3/products or /shopcarts/3/products?name=Settlers of Catan for querying for a product
@app.route('/shopcarts/<int:sid>/products', methods=['GET'])
def get_products(sid):
    carts = [cart for cart in shopping_carts if cart['sid']==sid]
    name = request.args.get('name')
    if len(carts) > 0:
        products = carts[0]['products']
        if(len(products)==0):
            if name:
                message={ 'error' : 'Product with name: %s was not found' % urllib.unquote(name) }
                rc=HTTP_404_NOT_FOUND
            else:
                message='The cart contains no products'
                rc = HTTP_200_OK
        else:
            if name:
                if name.startswith('"') and name.endswith('"'):
                    name = name[1:-1]

                message=[product for product in products if product['name'].lower()==urllib.unquote(name).lower()]
                if len(message)==0:
                    message={ 'error' : 'Product with name: %s was not found' % urllib.unquote(name) }
                    rc=HTTP_404_NOT_FOUND
                else:
                    message=message[0]
                    rc = HTTP_200_OK
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
# USAGE: /shopcarts/3/products/114672050
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


######################################################################
# ADD A NEW SHOPPING CART
######################################################################
@app.route('/shopcarts', methods=['POST'])
def create_shopcarts():

    payload = request.get_json()
    if Shopcart.validate_shopcart(payload):
        valid_product = False
        shopping_cart_exists = False

        shopcart_found = Shopcart.find_by_uid(payload['uid'])

        if len(shopcart_found) > 0:
            message = { 'error' : 'Shopping Cart for uid %s already exists' %str(payload['uid']) }
            rc = HTTP_400_BAD_REQUEST
            shopping_cart_exists = True

        if shopping_cart_exists == False:
            if 'products' not in payload:
                payload['products'] = [[]]
                valid_product = True
            else:
                if Shopcart.validate_product(payload):
                    valid_product = True
                else:
                    message = { 'error' : 'Data is not valid' }
                    rc = HTTP_400_BAD_REQUEST

            if 'subtotal' not in payload:
                payload['subtotal'] = 0.0

            if valid_product == True:
                shopcart = Shopcart()
                shopcart.deserialize(payload)
                shopcart.save("shopcart")
                message = shopcart.serialize()
                headerLocation = shopcart.self_url("shopcart")
                rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST


    response = make_response(jsonify(message), rc)
    if rc == HTTP_201_CREATED:
        response.headers['Location'] = headerLocation
    return response

######################################################################
# ADD A NEW PRODUCT IN A SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>/products', methods=['POST'])
def create_products(sid):

    existing_shopcart = Shopcart.check_shopcart_exists(sid)

    if existing_shopcart:
        payload = request.get_json()
        if Shopcart.validate_product(payload):
            existing_shopcart.deserialize_products(payload['products'])
            existing_shopcart.save("product")
            message = existing_shopcart.serialize()
            headerLocation = existing_shopcart.self_url("product")
            rc = HTTP_201_CREATED
        else:
            message = { 'error' : 'Data is not valid' }
            rc = HTTP_400_BAD_REQUEST

        response = make_response(jsonify(message), rc)
        return response
    else:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND
        return make_response(jsonify(message), rc)

######################################################################
# UPDATE product in a shopping cart
######################################################################
@app.route('/shopcarts/<int:sid>/products/<int:sku>', methods=['PUT'])
def put_product(sid, sku):
    cart = [cart for cart in shopping_carts if cart['sid'] == sid]
    if len(cart) > 0:
        payload = request.get_json()
        products = payload['products']
        if is_valid_product(payload) and len(products) == 1:
            updated_product = {'sku': products[0]['sku'], 'quantity': products[0]['quantity'], 'name': products[0]['name'], 'unitprice': products[0]['unitprice']}

            found_product = False
            for i in range(len(cart[0]['products'])):
                product = cart[0]['products'][i]
                if product['sku'] == sku:
                    cart[0]['products'][i] = updated_product
                    found_product = True
                    break

            if found_product:
                message = cart[0]
                rc = HTTP_200_OK
            else:
                message = { 'error' : 'Product %s was not found in shopping cart %s' % (str(sku), str(sid)) }
                rc = HTTP_404_NOT_FOUND
        else:
            message = { 'error' : 'Product data is not valid' }
            rc = HTTP_400_BAD_REQUEST

        response = make_response(jsonify(message), rc)

    else:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND
        response = make_response(jsonify(message), rc)

    return response

######################################################################
# DELETE A SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>', methods=['DELETE'])
def delete_shopcarts(sid):
    for i in range(len(shopping_carts)):
    	if shopping_carts[i]['sid'] == sid:
    	    del shopping_carts[i]
    	    break
    return '', HTTP_204_NO_CONTENT

######################################################################
# DELETE A PRODUCT FROM A SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>/products/<int:sku>', methods=['DELETE'])
def delete_products(sid,sku):
    for i in range(len(shopping_carts)):
    	if shopping_carts[i]['sid'] == sid:
    	    for j in range(len(shopping_carts[i]['products'])):
    	    	if shopping_carts[i]['products'][j]['sku'] == sku:
    	    		del shopping_carts[i]['products'][j]
    	    		break
    return '', HTTP_204_NO_CONTENT

######################################################################
# ACTION SUBTOTAL OF SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>/subtotal', methods=['PUT'])
def subtotal_shopcart(sid):
    for i in range(len(shopping_carts)):
        if shopping_carts[i]['sid'] == sid:
            subtotal = 0.0

            for product in shopping_carts[i]['products']:
                subtotal += product['unitprice'] * product['quantity']
            shopping_carts[i]['subtotal'] = float("{0:.2f}".format(subtotal))
            message = shopping_carts[i]
            rc = HTTP_200_OK
            break

    if not 'rc' in locals():
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND

    return make_response(jsonify(message), rc)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

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
# Connect to Redis and catch connection exceptions
######################################################################
def connect_to_redis(hostname, port, password):
    redis = Redis(host=hostname, port=port, password=password)
    try:
        redis.ping()
    except ConnectionError:
        redis = None
    return redis

######################################################################
# INITIALIZE Redis
# This method will work in the following conditions:
#   1) In Bluemix with Redis bound through VCAP_SERVICES
#   2) With Redis running on the local server as with Travis CI
#   3) With Redis --link ed in a Docker container called 'redis'
######################################################################
def inititalize_redis():
    global redis
    redis = None
    # Get the crdentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        app.logger.info("Using VCAP_SERVICES...")
        VCAP_SERVICES = os.environ['VCAP_SERVICES']
        services = json.loads(VCAP_SERVICES)
        creds = services['rediscloud'][0]['credentials']
        app.logger.info("Conecting to Redis on host %s port %s" % (creds['hostname'], creds['port']))
        redis = connect_to_redis(creds['hostname'], creds['port'], creds['password'])
    else:
        app.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
        redis = connect_to_redis('127.0.0.1', 6379, None)
        if not redis:
            app.logger.info("No Redis on localhost, using: redis")
            redis = connect_to_redis('redis', 6379, None)
    if not redis:
        # if you end up here, redis instance is down.
        app.logger.error('*** FATAL ERROR: Could not connect to the Redis Service')
    Shopcart.use_db(redis)
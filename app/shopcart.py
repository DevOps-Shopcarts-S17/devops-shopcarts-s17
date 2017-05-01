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
    docs_url = request.base_url + 'apidocs/index.html'
    return make_response(jsonify(name='Shopcart Demo REST API Service v1.0',
                   version='1.0',
                   url=shopcarts_url,
                   docs=docs_url
                   ), HTTP_200_OK)

######################################################################
# LIST ALL SHOPCARTS FOR ALL USERS
######################################################################
# USAGE: /shopcarts or /shopcarts?uid=1 for quering for a user
@app.route('/shopcarts', methods=['GET'])
def list_shopcarts():

    '''
    Retrieve a list of shopcarts
    This endpoint will return all Shopcarts unless a query parameter is specificed
    ---
    tags:
      - Shopcarts
    description: The Shopcarts endpoint allows you to query Shopcarts
    parameters:
      - name: uid
        in: query
        description: the uid of Shopcart you are looking for
        required: false
        type: string
    responses:
      200:
        description: An array of Shopcarts
        schema:
          type: array
          items:
            schema:
              id: Shopcart
              properties:
                    uid:
                        type: integer
                        description: unique id of the user of the shopcart
                    sid:
                        type: integer
                        description: unique id assigned internally by service
                    subtotal:
                        type: number
                        description: subtotal of all the products in the shopcart
                    products:
                        schema:
                          type: array
                          items:
                            schema:
                                id: Product
                                properties:
                                    sku:
                                        type: integer
                                        description: unique id of the particular product
                                    name:
                                        type: string
                                        description: name of the particular product
                                    quantity:
                                        type: integer
                                        description: quantity of the particular product
                                    unitprice:
                                        type: number
                                        description: price of the particular product

    '''
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

    """
    Retrieve a single shopcart
    This endpoint will return a Shopcart based on it's sid
    ---
    tags:
      - Shopcarts
    produces:
      - application/json
    parameters:
      - name: sid
        in: path
        description: sid of the shopcart to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Shopcart returned
        schema:
          id: Shopcart
          properties:
            uid:
              type: integer
              description: unique id of the user of the shopcart
            sid:
              type: integer
              description: unique id internally generated by the service
            subtotal:
              type: number
              description: subtotal of all the products in the shopcart
            products:
              schema:
                type: array
                items:
                  schema:
                      id: Product
                      properties:
                          sku:
                            type: integer
                            description: unique id of the particular product
                          name:
                            type: string
                            description: name of the particular product
                          quantity:
                            type: integer
                            description: quantity of the particular product
                          unitprice:
                            type: number
                            description: price of the particular product

      404:
        description: Shopcart not found
    """


    cart = Shopcart.find(sid)
    if cart:
        message = cart
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

    """
    Retrieve a list of products of a particular shopcart
    This endpoint will return all products of a shopcart unless a query parameter is specificed
    ---
    tags:
      - Shopcarts
    description: The Products endpoint allows you to query products
    parameters:
      - name: sid
        in: path
        description: the sid of the shopcart you are looking for
        required: true
        type: integer
      - name: name
        in: query
        description: the name of the product you are looking for
        required: false
        type: string
    responses:
      200:
        description: An array of Products
        schema:
          type: array
          items:
            schema:
              id: Product
              properties:
                sku:
                  type: integer
                  description: unique id of the particular product
                name:
                  type: string
                  description: name of the particular product
                quantity:
                  type: integer
                  description: quantity of the particular product
                unitprice:
                   type: number
                   description: price of the particular product
    """

    cart = Shopcart.find(sid)
    name = request.args.get('name')
    if cart:
        products = cart['products']
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
    cart = Shopcart.find(sid)
    if not cart:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        return make_response(jsonify(message),HTTP_404_NOT_FOUND)
    else:
        products=[product for product in cart['products'] if product['sku']==sku]
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

    """
    Creates a Shopcart
    This endpoint will create a Shopcart based the data in the body that is posted
    ---
    tags:
      - Shopcarts
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - uid
          optional:
            - subtotal
            - products
          properties:
            uid:
              type: integer
              description: name for the Pet
            subtotal:
              type: number
              description: subtotal of all the products in the shopcart
            products:
              schema:
                type: array
                items:
                  schema:
                      id: Product
                      properties:
                          sku:
                            type: integer
                            description: unique id of the particular product
                          name:
                            type: string
                            description: name of the particular product
                          quantity:
                            type: integer
                            description: quantity of the particular product
                          unitprice:
                            type: number
                            description: price of the particular product
    responses:
      201:
        description: Shopcart created
        schema:
          id: Shopcart
          properties:
            uid:
              type: integer
              description: unique id of the user of the shopcart
            sid:
              type: integer
              description: unique id internally generated by the service
            subtotal:
              type: number
              description: subtotal of all the products in the shopcart
            products:
              schema:
                type: array
                items:
                  schema:
                      id: Product
                      properties:
                          sku:
                            type: integer
                            description: unique id of the particular product
                          name:
                            type: string
                            description: name of the particular product
                          quantity:
                            type: integer
                            description: quantity of the particular product
                          unitprice:
                            type: number
                            description: price of the particular product
      400:
        description: Bad Request (the posted data was not valid)
    """

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
                shopcart.save()
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

    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    ---
    tags:
      - Shopcarts
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: sid
        in: path
        description: the sid of the shopcart to which you want to add products
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - sku
            - name
            - quantity
            - unitprice
          properties:
            sku:
                type: integer
                description: unique id of the particular product
            name:
                type: string
                description: name of the particular product
            quantity:
                type: integer
                description: quantity of the particular product
            unitprice:
                type: number
                description: price of the particular product
    responses:
      201:
        description: Product created
        schema:
          id: Product
          properties:
            sku:
                type: integer
                description: unique id of the particular product
            name:
                type: string
                description: name of the particular product
            quantity:
                type: integer
                description: quantity of the particular product
            unitprice:
                type: number
                description: price of the particular product
      400:
        description: Bad Request (the posted data was not valid)
    """

    existing_shopcart = Shopcart.check_shopcart_exists(sid)

    if existing_shopcart:
        payload = request.get_json()
        if Shopcart.validate_product(payload):
            existing_shopcart.deserialize_products(payload['products'])
            existing_shopcart.save()
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

    """
    Updates a Product
    This endpoint will update a Product based the data in the body that is posted
    ---
    tags:
      - Shopcarts
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: sid
        in: path
        description: the sid of the shopcart whose product you want to update
        required: true
        type: integer
      - name: sku
        in: path
        description: the sku of the product you are looking for
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - sku
            - name
            - quantity
            - unitprice
          properties:
            sku:
                type: integer
                description: unique id of the particular product
            name:
                type: string
                description: name of the particular product
            quantity:
                type: integer
                description: quantity of the particular product
            unitprice:
                type: number
                description: price of the particular product
    responses:
      200:
        description: Product updated
        schema:
          id: Product
          properties:
            sku:
                type: integer
                description: unique id of the particular product
            name:
                type: string
                description: name of the particular product
            quantity:
                type: integer
                description: quantity of the particular product
            unitprice:
                type: number
                description: price of the particular product
      400:
        description: Bad Request (the posted data was not valid)
    """

    cart = Shopcart.find(sid)
    if cart:
        payload = request.get_json()
        products = payload['products']
        if Shopcart.validate_product(payload) and len(products) == 1:
            updated_product = {'sku': products[0]['sku'], 'quantity': products[0]['quantity'], 'name': products[0]['name'], 'unitprice': products[0]['unitprice']}

            found_product = False
            for i in range(len(cart['products'])):
                product = cart['products'][i]
                if product['sku'] == sku:
                    cart['products'][i] = updated_product
                    found_product = True
                    break
                
            if found_product:
                s = Shopcart()
                s.deserialize(cart).save()
                message = cart
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

    """
    Delete a Shopcart
    This endpoint will delete a shopcart based the id specified in the path
    ---
    tags:
      - Shopcarts
    description: Deletes a Shopcart from the database
    parameters:
      - name: sid
        in: path
        description: sid of shopcart to delete
        type: integer
        required: true
    responses:
      204:
        description: Shopcart deleted
    """


    cart = Shopcart.find(sid)
    if cart:
        s = Shopcart()
        s.deserialize(cart).save()
        s.delete()
    return make_response('', HTTP_204_NO_CONTENT)

######################################################################
# DELETE A PRODUCT FROM A SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>/products/<int:sku>', methods=['DELETE'])
def delete_products(sid,sku):

    """
    Delete a Product
    This endpoint will delete a product based the sku specified in the path
    ---
    tags:
      - Shopcarts
    description: Deletes a product from a shopcart from the database
    parameters:
      - name: sid
        in: path
        description: sid of shopcart from which product needs to be deleted
        type: integer
        required: true
      - name: sku
        in: path
        description: sku of product to delete
        type: integer
        required: true
    responses:
      204:
        description: Product deleted
    """

    cart = Shopcart.find(sid)
    if cart:
        for j in range(len(cart['products'])):
            if cart['products'][j]['sku'] == sku:
                del cart['products'][j]
                break
        s = Shopcart()
        s.deserialize(cart).save()
    return '', HTTP_204_NO_CONTENT

######################################################################
# ACTION SUBTOTAL OF SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>/subtotal', methods=['PUT'])
def subtotal_shopcart(sid):

    """
    Calculates the subtotal of all the products in a Shopcart
    This endpoint will calculate the subtotal of a shopcart based on the id specified in the path
    ---
    tags:
      - Shopcarts
    description: Calculates subtotal of a shopcart
    parameters:
      - name: sid
        in: path
        description: sid of shopcart whose subtotal you want to calculate
        type: integer
        required: true
    responses:
      204:
        description: Subtotal calculated
    """

    cart = Shopcart.find(sid)

    if cart:
        subtotal = 0.0
        for product in cart['products']:
            subtotal += product['unitprice'] * product['quantity']
        cart['subtotal'] = float("{0:.2f}".format(subtotal))
        shopcart = Shopcart()
        shopcart.deserialize(cart).save()
        message = cart
        rc = HTTP_200_OK

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
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
    shopcarts_url = request.base_url + "shopcarts"
    return make_response(jsonify(name='Shopcart Demo REST API Service v1.0',
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
# UPDATE product in a shopping cart
######################################################################
@app.route('/shopcarts/<int:sid>/products/<int:sku>', methods=['PUT'])
def put_product(sid, sku):
    cart = [cart for cart in shopping_carts if cart['sid'] == sid]
    if len(cart) > 0:
        payload = request.get_json()
        products = payload['products']

        if is_validProduct(payload) and len(products) == 1:
            updated_product = {'sku': products[0]['sku'], 'quantity': products[0]['quantity'], 'name': products[0]['name'], 'unitprice': products[0]['unitprice']}
            print(updated_product)

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

        if rc == HTTP_201_CREATED:
            response.headers['Location'] = url_for('put_product', sku = payload['sku'], sid=shopping_carts[cart[0].sid])
        return response

    else:
        message = { 'error' : 'Shopping Cart with id: %s was not found' % str(sid) }
        rc = HTTP_404_NOT_FOUND
        return make_response(jsonify(message), rc)

######################################################################
# DELETE A PRODUCT FROM A SHOPPING CART
######################################################################
@app.route('/shopcarts/<int:sid>/products/<int:sku>', methods=['DELETE'])
def delete_products(sid,sku):
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

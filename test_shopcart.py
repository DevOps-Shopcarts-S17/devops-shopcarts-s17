# python -m unittest discover
# coverage run test_shopcart.py
# coverage report -m --include=shopcart.py

import unittest
import json
import logging
from flask_api import status    # HTTP Status Codes
from app import shopcart as server
from app.models import Shopcart

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopcartServer(unittest.TestCase):

    def setUp(self):
        # Only log criticl errors
        server.inititalize_redis()
        server.app.debug = True
        server.app.logger.addHandler(logging.StreamHandler())
        server.app.logger.setLevel(logging.CRITICAL)
        shopping_carts = [
            {
                'uid':1,
                'sid':  1,
                'subtotal': 0.00,
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
                'subtotal': 0.00,
                'products': []
            },
            {
                'uid': 3,
                'sid': 3,
                'subtotal': 0.00,
                'products': [
                    {
                        'sku': 114672050,
                        'quantity': 1,
                        'name': "Game of Life",
                        'unitprice': 13.99
                    }
                ]
            }
        ]
        Shopcart.remove_all()
        for s in shopping_carts:
            shopcart = Shopcart()
            shopcart.deserialize(s).save()
        self.app = server.app.test_client()

    def test_index(self):
        resp = self.app.get('/')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertTrue ('Shopcart Demo REST API Service' in resp.data)

    def test_list_shopcarts(self):
        resp = self.app.get('/shopcarts')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 )

    def test_list_shopcarts_uid_param(self):
        resp = self.app.get('/shopcarts?uid=1')
        self.assertEqual( resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 4)
        self.assertTrue(data['uid'] == 1)

    def test_list_shopcarts_uid_invalid(self):
        resp = self.app.get('/shopcarts?uid=abc')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 1)
        self.assertEqual(data['error'], 'Data is not valid')

    def test_list_shopcarts_uid_nonexist(self):
        resp = self.app.get('/shopcarts?uid=10')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 1)
        self.assertEqual(data['error'], 'Shopping Cart under user id: %s was not found' % 10)

    def test_get_shopcart(self):
        resp = self.app.get('/shopcarts/3')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEqual (data['products'][0]['name'], 'Game of Life')

    def test_get_shopcart_not_found(self):
        resp = self.app.get('/shopcarts/0')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )

    def test_get_product_sid_exist_product_sku_exist(self):
        resp = self.app.get('/shopcarts/1/products/876543210')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue ( len(resp.data) > 0 )

    def test_get_product_sid_exist_product_sku_nonexist(self):
        resp = self.app.get('/shopcarts/3/products/876543210')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )
        data = json.loads(resp.data)
        self.assertTrue ( 'Product with sku: 876543210 was not found in the cart for user 3' in resp.data )

    def test_get_products(self):
        resp = self.app.get('/shopcarts/2/products')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )

    def test_get_products_empty(self):
        resp = self.app.get('/shopcarts/2/products')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( resp.data, '"The cart contains no products"\n' )

    def test_get_products_sid_nonexist(self):
        resp = self.app.get('/shopcarts/47/products')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 1)
        self.assertTrue(data['error'] == "Shopping Cart with id: 47 was not found")

    def test_get_products_name(self):
        resp = self.app.get('/shopcarts/1/products?name=Settlers of Catan')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue(data['name'] == "Settlers of Catan")

    def test_get_products_name_with_quotes(self):
        resp = self.app.get('/shopcarts/3/products?name=\"Game of Life\"')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue(data['name'] == "Game of Life")

    def test_get_products_name_empty(self):
        resp = self.app.get('/shopcarts/2/products?name=Catan Expansion Pack')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 1)
        self.assertTrue(data['error'] == "Product with name: Catan Expansion Pack was not found")

    def test_get_products_name_nonexist(self):
        resp = self.app.get('/shopcarts/3/products?name=Catan Expansion Pack')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertTrue(len(data) == 1)
        self.assertTrue(data['error'] == "Product with name: Catan Expansion Pack was not found")

    def test_get_product_sid_nonexist(self):
        resp = self.app.get('/shopcarts/0/products/123456780')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )
        data = json.loads(resp.data)
        self.assertTrue ( 'Shopping Cart with id: 0 was not found' in resp.data )

    def test_get_subtotal_invalid_sid(self):
        resp = self.app.put('/shopcarts/0/subtotal')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )
        data = json.loads(resp.data)
        self.assertTrue ( 'Shopping Cart with id: 0 was not found' in resp.data )

    def test_get_subtotal_valid_sid(self):
        resp = self.app.put('/shopcarts/3/subtotal')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertEqual( data['subtotal'], 13.99)


    def test_create_shopcart_without_products(self):
        # save the current number of shopcarts for later comparrison
        shopcart_count = self.get_shopcart_count()
        # add a new valid shopcart
        new_shopcart = {"uid": 15}
        data = json.dumps(new_shopcart)
        resp = self.app.post('/shopcarts', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_201_CREATED )
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual (new_json['uid'], 15)
        # check that list of shopcarts has been updated and has a new shopcart
        resp = self.app.get('/shopcarts/'+str(server.current_shopping_cart_id))
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )

        # save the current number of products for later comparrison
        initial_product_count = self.get_product_count_by_shopcart(server.current_shopping_cart_id)
        # add a new valid product to an valid shopcart
        new_product = { "products": [{"sku" : 114672050, "quantity" : 665555, "name" : "Lego" , "unitprice" : 43.12}, {"sku" : 114342051, "quantity" : 4, "name" : "Taboo" , "unitprice" : 3.76}] }
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts/'+str(server.current_shopping_cart_id)+'/products', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_201_CREATED )
        new_json = json.loads(resp.data)

        for i in range(0,len(new_json['products'])):
            if new_json['products'][i]['sku'] == 114672052:
                self.assertEqual (new_json['products'][i]['quantity'], 665555)
                self.assertEqual (new_json['products'][i]['name'], "Lego")
                self.assertEqual (new_json['products'][i]['unitprice'], 43.12)
            elif new_json['products'][i]['sku'] == 114342051:
                self.assertEqual (new_json['products'][i]['quantity'], 4)
                self.assertEqual (new_json['products'][i]['name'], "Taboo")
                self.assertEqual (new_json['products'][i]['unitprice'], 3.76)

        # check that list of products has been updated and has the new product
        resp = self.app.get('/shopcarts/'+str(server.current_shopping_cart_id)+'/products')
        product_count = self.check_product_quantity(resp)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( product_count, initial_product_count + 2)

    def test_create_shopcart_empty_json(self):
        # save the current number of shopcarts for later comparrison
        shopcart_count = self.get_shopcart_count()
        # add a new invalid shopcart
        new_shopcart = {}
        data = json.dumps(new_shopcart)
        resp = self.app.post('/shopcarts', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        # check that the list of shopcarts has not been updated and does not have a new shopcart
        resp = self.app.get('/shopcarts')
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( len(data), shopcart_count)

    def test_create_shopcart_invalid_json(self):
        # save the current number of shopcarts for later comparrison
        shopcart_count = self.get_shopcart_count()
        # add a new invalid shopcart
        new_shopcart = { "uid": 6, "products": {"hi":"hello"} }
        data = json.dumps(new_shopcart)
        resp = self.app.post('/shopcarts', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        # check that the list of shopcarts has not been updated and does not have a new shopcart
        resp = self.app.get('/shopcarts')
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( len(data), shopcart_count)

    def test_create_shopcart_bad_json(self):
        # save the current number of shopcarts for later comparrison
        shopcart_count = self.get_shopcart_count()
        # add a new invalid shopcart
        new_shopcart = "uid : 6"
        data = json.dumps(new_shopcart)
        resp = self.app.post('/shopcarts', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        # check that the list of shopcarts has not been updated and does not have a new shopcart
        resp = self.app.get('/shopcarts')
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( len(data), shopcart_count)

    def test_create_shopcart_existing_sid(self):
        # save the current number of shopcarts for later comparrison
        shopcart_count = self.get_shopcart_count()
        # add a new invalid shopcart
        new_shopcart = {"uid": 1}
        data = json.dumps(new_shopcart)
        resp = self.app.post('/shopcarts', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        # check that the list of shopcarts has not been updated and does not have a new shopcart
        resp = self.app.get('/shopcarts')
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( len(data), shopcart_count)


    def test_create_valid_shopcart_only_sid_json(self):
        # save the current number of shopcarts for later comparrison
        shopcart_count = self.get_shopcart_count()
        # add a new valid shopcart
        new_shopcart = {"uid": 5}
        data = json.dumps(new_shopcart)
        resp = self.app.post('/shopcarts', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_201_CREATED )
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual (new_json['uid'], 5)
        # check that list of shopcarts has been updated and has a new shopcart
        resp = self.app.get('/shopcarts')
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( len(data), shopcart_count + 1 )
        self.assertIn( new_json, data )

    def test_create_shopcarts_valid_complete_json(self):
        # save the current number of shopcarts for later comparrison
        shopcart_count = self.get_shopcart_count()
        # add a new valid shopcart
        new_shopcart = { "uid": 6, "products": [{"sku" : 114672050, "quantity" : 665555, "name" : "Lego" , "unitprice" : 43.12}, {"sku" : 114342051, "quantity" : 4, "name" : "Taboo" , "unitprice" : 3.76}] }
        data = json.dumps(new_shopcart)
        resp = self.app.post('/shopcarts', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_201_CREATED )
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual (new_json['uid'], 6)
        # check that list of shopcarts has been updated and has a new shopcart
        resp = self.app.get('/shopcarts')
        data = json.loads(resp.data)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( len(data), shopcart_count + 1 )
        self.assertIn( new_json, data )

    def test_create_products_empty_json(self):
        # save the current number of products for later comparrison
        initial_product_count = self.get_product_count_by_shopcart(2)
        # add a new invalid product
        new_product = {}
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts/2/products', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        # check that the list of products has not been updated and does not have a new product
        resp = self.app.get('/shopcarts/2/products')
        product_count = self.check_product_quantity(resp)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( product_count, initial_product_count)

    def test_create_products_bad_json(self):
        # save the current number of products for later comparrison
        initial_product_count = self.get_product_count_by_shopcart(2)
        # add a new invalid product
        new_product = "products: [{sku : 114672050, quantity : 665555, name : Lego , unitprice : 43.12}]"
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts/2/products', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        # check that the list of products has not been updated and does not have a new product
        resp = self.app.get('/shopcarts/2/products')
        product_count = self.check_product_quantity(resp)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( product_count, initial_product_count)

    def test_create_products_invalid_json(self):
        # save the current number of products for later comparrison
        initial_product_count = self.get_product_count_by_shopcart(2)
        # add a new invalid product
        new_product = { "products": [{"sku" : 114672050, "quantity" : 665555, "name" : "Lego" , "unitprice" : 43.12}, {"sku" : 114342051, "quantity" : 4, "name" : "Taboo"}] }
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts/2/products', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_400_BAD_REQUEST )
        # check that the list of products has not been updated and does not have a new product
        resp = self.app.get('/shopcarts/2/products')
        product_count = self.check_product_quantity(resp)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( product_count, initial_product_count)

    def test_create_products_invalid_shopcart(self):
        # save the current number of products for later comparrison
        initial_product_count = self.get_product_count_by_shopcart(2)
        # add a new valid product to an invalid shopcart
        new_product = { "products": [{"sku" : 114672052, "quantity" : 665555, "name" : "Lego" , "unitprice" : 43.12}, {"sku" : 114342051, "quantity" : 4, "name" : "Taboo" , "unitprice" : 3.76}] }
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts/35/products', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )

    def test_create_products_valid_json(self):
        # save the current number of products for later comparrison
        initial_product_count = self.get_product_count_by_shopcart(2)
        # add a new valid product to an valid shopcart
        new_product = { "products": [{"sku" : 114672050, "quantity" : 665555, "name" : "Lego" , "unitprice" : 43.12}, {"sku" : 114342051, "quantity" : 4, "name" : "Taboo" , "unitprice" : 3.76}] }
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts/2/products', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_201_CREATED )
        new_json = json.loads(resp.data)

        for i in range(0,len(new_json['products'])):
            if new_json['products'][i]['sku'] == 114672052:
                self.assertEqual (new_json['products'][i]['quantity'], 665555)
                self.assertEqual (new_json['products'][i]['name'], "Lego")
                self.assertEqual (new_json['products'][i]['unitprice'], 43.12)
            elif new_json['products'][i]['sku'] == 114342051:
                self.assertEqual (new_json['products'][i]['quantity'], 4)
                self.assertEqual (new_json['products'][i]['name'], "Taboo")
                self.assertEqual (new_json['products'][i]['unitprice'], 3.76)

        # check that list of products has been updated and has the new product
        resp = self.app.get('/shopcarts/2/products')
        product_count = self.check_product_quantity(resp)
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertEqual( product_count, initial_product_count + 2)

    def test_delete_shopcarts_exist(self):
        # save the current number of shopcarts for later comparison
        shopcart_count = self.get_shopcart_count()
        # delete a shopcart that exists
        resp = self.app.delete('/shopcarts/2', content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_204_NO_CONTENT )
        self.assertEqual( len(resp.data), 0 )
        new_count = self.get_shopcart_count()
        self.assertEqual( new_count, shopcart_count - 1)

    def test_delete_shopcarts_nonexist(self):
        # save the current number of shopcarts for later comparison
        shopcart_count = self.get_shopcart_count()
        # delete a shopcart that doesn't exist
        resp = self.app.delete('/shopcarts/0', content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_204_NO_CONTENT )
        self.assertEqual( len(resp.data), 0 )
        new_count = self.get_shopcart_count()
        self.assertEqual( new_count, shopcart_count )

    def test_delete_product_exist(self):
        # assuming shopcarts/1/products is not empty.
        # save the current number of products for later comparison
        shopcart_count = self.get_product_count_by_shopcart(1)
        # delete a product that exists
        resp = self.app.delete('/shopcarts/1/products/123456780', content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_204_NO_CONTENT )
        self.assertEqual( len(resp.data), 0 )
        new_count = self.get_product_count_by_shopcart(1)
        self.assertEqual( new_count, shopcart_count - 1)

    def test_delete_product_valid_shopcart_invalid_product(self):
        # assuming shopcarts/1/products is not empty.
        # save the current number of products for later comparison
        shopcart_count = self.get_product_count_by_shopcart(1)
        # delete a product that doesn't exist
        resp = self.app.delete('/shopcarts/1/products/111111111', content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_204_NO_CONTENT )
        self.assertEqual( len(resp.data), 0 )
        new_count = self.get_product_count_by_shopcart(1)
        self.assertEqual( new_count, shopcart_count )

    def test_delete_product_invalid_shopcart_invalid_product(self):
        # assuming shopcarts/10 not exist.
        resp = self.app.delete('/shopcarts/10/products/111111111', content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_204_NO_CONTENT )
        self.assertEqual( len(resp.data), 0 )

    def test_put_product_valid_shopcart_valid_product(self):
        product_new_information = {
	       "products": [
		       {
			       "name": "Settlers of Catan",
			       "quantity": 15,
			       "sku": 123456780,
			       "unitprice": 28.99
		       }
	        ]
        }
        data = json.dumps(product_new_information)
        resp = self.app.put('/shopcarts/1/products/123456780', data=data, content_type='application/json')
        self.assertTrue( len(resp.data) > 0)
        cart = json.loads(resp.data)
        self.assertTrue( cart is not None and "products" in cart and cart["products"] is not None)
        for product in cart["products"]:
            if product["sku"] == 123456780:
                self.assertEqual(product["unitprice"], 28.99)
                self.assertEqual(product["quantity"], 15)

    def test_put_product_change_sku(self):
        product_new_information = {
	       "products": [
		       {
			       "name": "Settlers of Catan",
			       "quantity": 2,
			       "sku": 123456789,
			       "unitprice": 27.99
		       }
	        ]
        }
        data = json.dumps(product_new_information)
        resp = self.app.put('/shopcarts/1/products/123456780', data=data, content_type='application/json')
        self.assertTrue( len(resp.data) > 0)
        cart = json.loads(resp.data)
        self.assertTrue( cart is not None and "products" in cart and cart["products"] is not None)
        found_new_sku = False
        for product in cart["products"]:
            if product["sku"] == 123456789:
                found_new_sku = True
                self.assertEqual(product["name"], "Settlers of Catan")
        self.assertTrue(found_new_sku)
        # old sku should be invalid
        resp = self.app.get('/shopcarts/1/products/123456780')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )
        # new sku should valid
        resp = self.app.get('/shopcarts/1/products/123456789')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )

    def test_put_product_valid_shopcart_invalid_product(self):
        product_new_information = {
	       "products": [
		       {
			       "name": "Settlers of Catan",
			       "quantity": 1,
			       "sku": 123456789,
			       "unitprice": 27.99
		       }
	        ]
        }
        data = json.dumps(product_new_information)
        resp = self.app.put('/shopcarts/1/products/123456789', data=data, content_type='application/json')
        self.assertTrue( len(resp.data) > 0)
        self.assertTrue("Product 123456789 was not found" in resp.data)

    def test_put_product_invalid_shopcart_invalid_product(self):
        product_new_information = {
	       "products": [
		       {
			       "name": "Settlers of Catan",
			       "quantity": 1,
			       "sku": 123456789,
			       "unitprice": 27.99
		       }
	        ]
        }
        data = json.dumps(product_new_information)
        resp = self.app.put('/shopcarts/10/products/123456789', data=data, content_type='application/json')
        self.assertTrue( len(resp.data) > 0)
        self.assertTrue("Shopping Cart with id: 10 was not found" in resp.data)

    def test_put_product_invalid_json(self):
        product_new_information = {
	       "products": [
		       {
			       "name": "Settlers of Catan",
			       "quantity": 1,
			       "sku_id": 123456780,
			       "unitprice": 27.99
		       }
	        ]
        }
        data = json.dumps(product_new_information)
        resp = self.app.put('/shopcarts/1/products/123456780', data=data, content_type='application/json')
        self.assertTrue( len(resp.data) > 0)
        self.assertTrue("Product data is not valid" in resp.data)


######################################################################
# Utility functions
######################################################################

    def get_shopcart_count(self):
        # save the current number of shopcarts
        resp = self.app.get('/shopcarts')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        return len(data)

    def check_product_quantity(self,resp):
        data = json.loads(resp.data)
        if resp.data == '"The cart contains no products"\n':
            return 0
        else:
            if data[0]==[]:
                return 0
            else:
                return len(data)

    def get_product_count_by_shopcart(self, shopcart_id):
        resp = self.app.get('/shopcarts/%s/products' % str(shopcart_id))
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        product_count = self.check_product_quantity(resp)
        return product_count

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

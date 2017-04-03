# python -m unittest discover
# coverage run test_shopcart.py
# coverage report -m --include=shopcart.py

import unittest
import json
import logging
from flask_api import status    # HTTP Status Codes
import shopcart as server

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopcartServer(unittest.TestCase):

    def setUp(self):
        # Only log criticl errors
        server.app.debug = True
        server.app.logger.addHandler(logging.StreamHandler())
        server.app.logger.setLevel(logging.CRITICAL)
        self.app = server.app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        resp = self.app.get('/')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertTrue ('Shopcart Demo REST API Service' in resp.data)

    def test_list_shopcarts(self):
        resp = self.app.get('/shopcarts')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 )

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
        initial_product_count = self.get_product_count()
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
        initial_product_count = self.get_product_count()
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
        initial_product_count = self.get_product_count()
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
        initial_product_count = self.get_product_count()
        # add a new valid product to an invalid shopcart
        new_product = { "products": [{"sku" : 114672052, "quantity" : 665555, "name" : "Lego" , "unitprice" : 43.12}, {"sku" : 114342051, "quantity" : 4, "name" : "Taboo" , "unitprice" : 3.76}] }
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts/35/products', data=data, content_type='application/json')
        self.assertEqual( resp.status_code, status.HTTP_404_NOT_FOUND )

    def test_create_products_valid_json(self):
        # save the current number of products for later comparrison
        initial_product_count = self.get_product_count()
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

######################################################################
# Utility functions
######################################################################

    def get_shopcart_count(self):
        # save the current number of shopcarts
        resp = self.app.get('/shopcarts')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        data = json.loads(resp.data)
        return len(data)

    def get_product_count(self):
        # save the current number of products
        resp = self.app.get('/shopcarts/2/products')
        self.assertEqual( resp.status_code, status.HTTP_200_OK )
        product_count = self.check_product_quantity(resp)
        return product_count

    def check_product_quantity(self,resp):
        data = json.loads(resp.data)
        if resp.data == '"The cart contains no products"\n':
            return 0
        else:
            return len(data)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

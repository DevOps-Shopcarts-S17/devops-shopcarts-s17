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
class TestPetServer(unittest.TestCase):

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


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()

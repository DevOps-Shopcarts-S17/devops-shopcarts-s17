from behave import *
import shopcart as server

def before_all(context):
    context.app = server.app.test_client()
    server.shopping_carts = [
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
    server.current_shopping_cart_id = 3
    context.server = server

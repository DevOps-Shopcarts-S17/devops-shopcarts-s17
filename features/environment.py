from behave import *
from app import shopcart as server

def before_all(context):
    context.app = server.app.test_client()
    server.inititalize_redis() 
    context.server = server

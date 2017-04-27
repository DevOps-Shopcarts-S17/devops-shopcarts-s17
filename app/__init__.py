from flask import Flask

# Create the Flask aoo
app = Flask(__name__)

import shopcart as server
import models
import custom_exceptions
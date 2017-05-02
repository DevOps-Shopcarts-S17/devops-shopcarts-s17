import os
from app import app
from app import shopcart as server

# Pull options from environment
debug = (os.getenv('DEBUG', 'False') == 'True')
port = os.getenv('PORT', '8888')

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "Shopcart Service Starting..."
    server.inititalize_redis()
    app.run(host='0.0.0.0', port=int(port), debug=debug)

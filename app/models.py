import pickle
from flask import url_for
from werkzeug.exceptions import NotFound
from custom_exceptions import DataValidationError
from . import app

######################################################################
# Shopcart Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################

class Shopcart(object):
    __redis = None

    def __init__(self, uid=0, sid=0,subtotal=0.0,products=[]):
        self.uid = int(uid)
        self.sid = int(sid)
        self.subtotal = float(subtotal)
        self.products = products

    def save(self):
        if self.sid == 0:
            self.sid = self.__next_index()
        Shopcart.__redis.set(self.sid, pickle.dumps(self.serialize()))

    def __next_index(self):
        return Shopcart.__redis.incr('index')

    def self_url(self,urltype):
        if urltype == "shopcart":
            return url_for('get_shopcart', sid=self.sid, _external=True)
        elif urltype == "product":
            return url_for('get_product', sid=self.sid, _external=True)

    def serialize(self):
        return { "uid": self.uid, "sid": self.sid, "subtotal": self.subtotal, "products": self.products }

    def deserialize(self, data):
        if "sid" in data:
            self.sid = data['sid']
        self.uid = data['uid']
        self.subtotal = data['subtotal']
        self.products = data['products']
        return self

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @staticmethod
    def use_db(redis):
        Shopcart.__redis = redis

    @staticmethod
    def remove_all():
        Shopcart.__redis.flushall()

    @staticmethod
    def all():
        results = []
        for key in Shopcart.__redis.keys():
            if key != 'index':  # filer out our id index
                print key
                data = Shopcart.__redis.get(key)
                data = pickle.loads(data)
                results.append(data)
        return results

    @staticmethod
    def find(sid):
        if Shopcart.__redis.exists(sid):
            data = Shopcart.__redis.get(sid)
            data = pickle.loads(data)
            return data
        else:
            return None

    @staticmethod
    def check_shopcart_exists(data):
        if Shopcart.__redis.exists(data['uid']):
            return True
        else:
            return False

    @staticmethod
    def validate_shopcart(data):
        valid = False
        try:
            user_id = data['uid']
            valid = True
        except KeyError as err:
            raise DataValidationError('Missing parameter error: ' + err.args[0])
        except TypeError as err:
            raise DataValidationError('Invalid Content Type error: ' + err)
        return valid

    @staticmethod
    def validate_product(data):
        valid = False
        try:
            for i in range(0,len(data['products'])):
                sku = data['products'][i]['sku']
                quantity = data['products'][i]['quantity']
                name = data['products'][i]['name']
                unitprice = data['products'][i]['unitprice']
            valid = True
        except KeyError as err:
            valid = False
            #raise DataValidationError('Missing parameter error: ' + err.args[0])
        except TypeError as err:
            valid = False
            #raise DataValidationError('Invalid Content Type error: ' + err)
        return valid

    @staticmethod
    def find_by_uid(uid):
        # return [pet for pet in Pet.__data if pet.category == category]
        results = []
        for key in Shopcart.__redis.keys():
            if key != 'index':  # filer out our id index
                print key
                data = Shopcart.__redis.get(key)
                data = pickle.loads(data)
                if data["uid"] == uid:
                    results.append(data)
        return results
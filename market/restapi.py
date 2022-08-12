"""Orderbook market implementation

Orderbook API:

    GET /config

        Arguments:

            None

        Returns:

            quantity (str)
            price (str)

        Obtains the market configuration. The quantity value is the unit of quantity used
        and the price value is the quantity used for prices.  In general, the price unit 
        is the quantity unit multiplied by currency divided by time.

    GET /order

        Arguments:

            agent (str)
            quantity (str)
            price (str)

        Returns:

            id (str)
            agent (str)
            quantity (str)
            status (str)
            price (str)            

        Submit an order. If price is omitted, it is a market order. If price is included
        it is a limit order.  If quantity is negative it is a sell order. If quantity
        is positive it is a buy order. Quantity is not valid. If status is 'ACTIVE',
        the quantity is subtracted from the total quantity observation, if any.

    GET /users

        Arguments:

            pattern (str)

        Returns:

            id (str)
            name (str)

        Obtain a list users, optionally matching the pattern given for names.

    PUT /order

        Arguments:

            quantity (float)
            price (float)
            status (str)

        Returns:

            id (str)
            quantity (float)
            price (float)
            status (str)

    PATCH /order?id={str}&quantity={float}

    DELETE /order?id={str}
"""

import os, sys

import flask
assert(flask.__version__>"2")
from flask import Flask, request
from flask_restful import Resource, Api

import pandas as pd

from orderbook import Orderbook

#
# SERVER
#

app = Flask(__name__)
api = Api(app)

#
# DATA
#

def load_data():
    for name in DATA.keys():
        file = name + "s.csv"
        DATA[name] = pd.read_csv(file,dtype="str").set_index(f"{name}_id").to_dict("index")

def save_data(file):
    raise Exception("not implemented")

DATA = {
    "user" : {},
    "agent" : {},
}

load_data()

class Admin(Resource):

    def get(self):
        load_data()
        return {'data':DATA}, 200

    def put(self):
        save_data()
        return {'data':'ok'}, 200

api.add_resource(Admin,"/admin")

#
# USERS
#

class Users(Resource):
    def get(self):
        data = DATA["user"]
        return {'data': data}, 200  # return data and 200 OK code

api.add_resource(Users,"/users")

class User(Resource):

    def get(self,user_id):
        """GET"""
        if not user_id in DATA["user"].keys():
            return {'message' : "not found"}, 404
        return {'data': DATA["user"][user_id]}, 200  # return data and 200 OK code
    
    def post(self,user_id):
        name = request.form.get('name')
        DATA["user"][user_id] = {'name':name}
        return {'data':DATA["user"][user_id]},200

    def delete(self):
        pass
    
api.add_resource(User,"/user/<string:user_id>")

#
# AGENTS
#

class Agent(Resource):

    def __init__(self,name):

        self.id = self.next_id
        self.next_id += 1
        self.name = name

api.add_resource(Agent,"/agent/<string:agent_id>")

#
# ORDERS
#

ORDERS = Orderbook()
ORDERS.load("orders.csv")

class Orders(Resource):
    def get(self):
        return {'data': ORDERS.dump()}, 200  # return data and 200 OK code

api.add_resource(Orders,"/orders")

class Order(Resource):

    def get(self,order_id):
        return {'data':ORDERS.get(order_id)}, 200

    def post(self,order_id):
        agent_id = request.form.get('agent_id')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        insert_order(order_id=order_id,agent_id=agent_id,price=price,quantity=quantity)
        return {'data':DATA["order"][order_id]}, 200

api.add_resource(Order,"/order/<string:order_id>")

#
# ORDERBOOK
#

class Orderbook:

    def __init__(self):

        self.orders = None
        self.file = None

    def load(self,file):

        self.orders = pd.read_csv(file,index_col="order_id")

    def save(self,file=None):
        if not file:
            file = self.file
        self.orders.to_csv(file,header=True,index=True)

    def dump(self):

        return self.orders.to_dict(orient="index")

    def add(self,order_id,agent_id,price=None,quantity=None):

        pass

    def get(self,order_id):

        return self.orders.loc[order_id].to_dict(orient="index")
    
    def delete(self,order_id):

        pass

if __name__ == "__main__":

    app.run()
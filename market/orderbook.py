"""Orderbook implementation
"""

import sys
from collections import OrderedDict
import json
from order import *
from agent import *

class OrderbookError(Exception):
    pass

class Orderbook:

    version = 1.0

    default_config = {
        "price_cap" : 10000.0,
        "price_floor" : 0.0,
        "price_unit" : "$/MWh",
        "quantity_unit" : "MW",
        "margin" : True,
        "verbose" : False, # output verbose messages
        "quiet" : False,
        "warning" : False,
        "debug" : False,
        "database" : None,
    }

    def __init__(self,**kwargs):
        """Create an order book"""

        # configuration
        self.config = self.default_config
        for key,value in kwargs.items():
            if key in self.config.keys():
                self.config[key] = value
        for key,value in self.config.items():
            if key in kwargs.keys():
                del kwargs[key]
            self.verbose(f"config.{key} = {value}")

        # demand book
        if 'demand' in kwargs.keys():
            self.demand = OrderedDict(kwargs['demand'])
        else:
            self.demand = OrderedDict()
        self.verbose(f"demand = {json.dumps(self.demand)}")

        # supply book
        if 'supply' in kwargs.keys():
            self.supply = OrderedDict(kwargs['supply'])
        else:
            self.supply = OrderedDict()
        self.verbose(f"supply = {json.dumps(self.supply)}")

    def verbose(self,msg):
        """Output verbose message"""
        if self.config["verbose"]:
            print(f"VERBOSE [{__name__}.{self.__class__.__name__}]: {msg}",file=sys.stderr)

    def error(self,msg):
        """Output error message"""
        if not self.config["quiet"]:
            print(f"ERROR [{__name__}.{self.__class__.__name__}]: {msg}",file=sys.stderr)
        if self.config["debug"]:
            raise OrderbookError(msg)
        return None

    def warning(self,msg):
        """Output error message"""
        if not self.config["quiet"]:
            print(f"WARNING [{__name__}.{self.__class__.__name__}]: {msg}",file=sys.stderr)

    def add_order(self,**kwargs):
        """Add an order to the book"""
        if not 'quantity' in kwargs.keys():
            return self.error(f"add_order({kwargs}) order missing quantity")
        elif 'price' in kwargs.keys(): # limit order
            if kwargs['quantity'] < 0: # buy limit
                return self.add_demand_limit(**kwargs)
            elif kwargs['quantity'] > 0: # sell limit
                return self.add_supply_limit(**kwargs)
            else:
                return self.error(f"add_order({kwargs}) limit order with zero quantity")
        else: # market order
            if kwargs['quantity'] < 0: # buy limit
                return self.add_demand_market(**kwargs)
            elif kwargs['quantity'] > 0: # sell limit
                return self.add_supply_market(**kwargs)
            else:
                return self.error(f"add_order({kwargs}) market order with zero quantity")

    def add_demand_limit(self,quantity,price):
        if float(price) in self.demand.keys():
            self.demand[price] -= float(quantity)
        else:
            self.demand[price] = -float(quantity)
        self.verbose(f"add_demand_limit(quantity={quantity},price={price}): {self.demand[price]} {self.config['quantity_unit']} at {price} {self.config['price_unit']}")
        return self.dispatch(float(quantity),float(price))

    def add_supply_limit(self,quantity,price):
        if float(price) in self.supply.keys():
            self.supply[price] += float(quantity)
        else:
            self.supply[price] = float(quantity)
        self.verbose(f"add_supply_limit(quantity={quantity},price={price}): {self.supply[price]} {self.config['quantity_unit']} at {price} {self.config['price_unit']}")
        return self.dispatch(float(quantity),float(price))

    def add_demand_market(self,quantity):
        supply = list(self.supply.items())
        n = 0
        total = 0.0
        cost = 0.0
        while total < quantity:
            p = supply[n][0]
            d = q = supply[n][1]
            total += q
            if total > quantity:
                d -= total-quantity
                total = quantity
            cost += p * d
        return self.dispatch(float(quantity),float(cost/quantity))
        
    def add_supply_market(self,quantity):
        # TODO
        return self.dispatch(float(quantity))
                
    def dispatch(self,quantity,price=None):
        return dict(quantity=quantity,price=price)

    def to_dict(self,file=sys.stdout):
        return {"demand":self.demand,"supply":self.supply}

    def to_json(self,file=sys.stdout,indent=None):
        print(json.dumps(self.to_dict(),indent=indent),file=file)

    def supply_curve(self):
        x = []
        y = [0.0]
        q = 0.0
        p = 0.0
        for price,quantity in self.supply.items():
            y.extend([q,q+quantity])
            q += quantity
            x.extend([p,price])
            p = price
        y.append(q)
        x.extend([p,self.config['price_cap']])
        self.verbose(f"quantity x = {x}")
        self.verbose(f"price y = {y}")
        return x,y,p

    def demand_curve(self):
        x = []
        y = [0.0]
        q = 0.0
        p = 0.0
        for price,quantity in self.demand.items():
            y.extend([q,q+quantity])
            q += quantity
            x.extend([p,-price])
            p = -price
        y.append(q)
        x.extend([p,-self.config['price_cap']])
        self.verbose(f"price x = {x}")
        self.verbose(f"quantity y = {y}")
        return x,y,p

    def spread(self):
        return [-list(self.demand.keys())[0],list(self.supply.keys())[0]]

    def plot(self,filename=None,num=None,figsize=(7,5),dpi=160,title='auto'):
        """Plot the market

        Parameters:
            filename    specifies the file to save, default is use `show()`
            num         specifies the figure number to use, default is `None`
            figsize     specifies the figure size, default is `(7,5)`
            dpi         specifies the figure resolution, default is `160`
            title       specifies the image title, default is `auto`
        """
        import matplotlib.pyplot as plt 
        fig = plt.figure(num=num,figsize=figsize,dpi=dpi)

        # supply side
        x,y,ps = self.supply_curve()
        plt.plot(x,y,color='r')

        # demand side
        x,y,pd = self.demand_curve()
        plt.plot(x,y,color='b')

        # finalize
        plt.xlabel(f"Price {self.config['price_unit']}")
        plt.ylabel(f"Quantity {self.config['quantity_unit']}")
        plt.grid()
        plt.xlim([pd*1.1,ps*1.1])

        return fig

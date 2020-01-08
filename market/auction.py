"""Auction mechanism implementation

The auction solves buy/sell orders in a double auction.

Order may be added using add_order(quantity,price).
Buy orders have positive quantities and positive ids.
Sell orders have negative quantities and negative ids. 

To delete an order, use the order id returned by add_order(quantity,price).

To clear the market, use clear().  To plot a cleared market use plot(filename).

Example:

>>> import market.auction as auction
>>> a = auction(price_cap=10000.0)
>>> a.add_order(quantity=10,price=10)
1
>>> a.add_order(quantity=-10,price=10)
-1
>>> a.clear()
{'quantity':10,'price':10,'margin':None}
>>> a.plot('auction.png')

You may change the auction configuration using arguments passed to the auction
initialization. There are a number of configuration parameters that control the 
behavior of the auction.  They are

    price_cap     The maximum price accepted in an order (default is 10000)
    price_floor   The minimum price accepted in an order (default is 0)
    price_unit    The unit for prices (default is '$/MWh')
    quantity_unit The unit for quantities (default is 'MW')
    margin        Enables computation of the fraction of the marginal unit
    verbose       Enables verbose output during processing (default is False)

You may change the defaults by setting the value 'default_config', e.g.,

>>> auction.default_config["price_cap"] = 10000

"""

import datetime
try:
    import market.polyline as polyline
except:
    import polyline

class auction:

    default_config = {
        "price_cap" : 10000.0,
        "price_floor" : 0.0,
        "price_unit" : "$/MWh",
        "quantity_unit" : "MW",
        "margin" : False,
        "verbose" : False,
    }

    def __init__(self,**kwargs):
        self.config = self.default_config
        for key,value in kwargs.items():
            self.config[key] = value
        self.supply = []
        self.demand = []
        self.buy = None
        self.sell = None
        self.price = None
        self.quantity = None
        self.margin = None
        self.verbose(self.config)

    def verbose(self,msg):
        if self.get_config("verbose"):
            print(f"auction: {msg}")

    def get_config(self,name):
        """Get a configuration value"""
        if name in self.config.keys():
            return self.config[name]
        else:
            return None

    def add_order(self,quantity,price):
        """Add an order to the auction"""
        if price > self.get_config("price_cap"):
            raise Exception(f"order price={price} exceeds price_cap")
        if price < self.get_config("price_floor"):
            raise Exception(f"order price={price} below price_floor")
        if quantity < 0:
            self.supply.append((-float(quantity),float(price)))
            id = -len(self.supply)
            self.verbose(f"sell(quantity={-quantity},price={price}) -> id = {id}")
            return id
        elif quantity > 0:
            self.demand.append((float(quantity),float(price)))
            id = len(self.demand)
            self.verbose(f"buy(quantity={quantity},price={price}) -> id = {id}")
            return id
        else:
            raise Exception("quantity must be non-zero");

    def del_order(id):
        """Delete an order from the auction"""
        if id < 0 and -id+1 < len(self.supply):
            del self.supply[-id+1]
        elif id > 0 and id-1 < len(self.demand):
            del self.demand[id-1]
        else:
            raise Exception("order id is invalid")

    def clear(self):
        """Clear the market (meaning solve it)"""
        
        # sort orders by price
        buy_order = sorted(self.demand, key = lambda x: x[1],reverse=True)
        sell_order = sorted(self.supply, key = lambda x: x[1])
        self.verbose(f"buy_order={buy_order}")
        self.verbose(f"sell_order={sell_order}")

        # accumulate quantities
        def cumulative(curve,fill=None):
            q0 = 0.0
            if fill == 'buy':
                p0 = self.get_config("price_cap")
            elif fill == 'sell':
                p0 = self.get_config("price_floor")
            else:
                raise Exception("fill={'buy','sell'} not specified")
            result = [(q0,p0)]
            for order in curve:
                if order[1] != p0: # new vertex needed
                    result.append((q0,p0))
                    p0 = order[1]
                    result.append((q0,p0))
                q0 += order[0]
            if result[-1] != (q0,p0):
                result.append((q0,p0))
            if fill == 'sell' and result[-1][1] != self.get_config("price_cap"):
                result.append((q0,self.get_config("price_cap")))
            elif fill == 'buy' and result[-1][1] != self.get_config("price_floor"):
                result.append((q0,self.get_config("price_floor")))
            return result
        self.buy = cumulative(buy_order,fill='buy')
        self.sell = cumulative(sell_order,fill='sell')
        self.verbose(f"buy_curve={self.buy}")
        self.verbose(f"sell_curve={self.sell}")

        # find the clearing point
        result = polyline.intersection(self.buy,self.sell)
        if result:

            # resolve ambiguous clearing conditions
            if len(result) > 1 : # more than one clearing point found
                self.quantity = max([x[0] for x in result])
                self.price = sum([x[1] for x in result])/len(result)
            else: # single clearing point found
                self.quantity = result[0][0];
                self.price = result[0][1]

            # compute the clearing margin
            if self.config["margin"]:
                raise Exception("marginal unit dispatch is not supported yet")

        self.verbose(f"clear() -> {result}")
        return {"quantity":self.quantity,"price":self.price,"margin":self.margin};

    def plot(self,filename="auction.png",num=None,figsize=(7,5),dpi=160,title='auto'):
        """Plot the market"""
        import matplotlib.pyplot as plt 
        plt.figure(num=num,figsize=figsize,dpi=dpi);
        if self.buy:
            qb = [x[0] for x in self.buy]
            pb = [x[1] for x in self.buy]
            self.verbose(f"plot(q={qb},p={pb},'b')")
            plt.plot(qb,pb,'b')
        if self.sell:
            qs = [x[0] for x in self.sell]
            ps = [x[1] for x in self.sell]
            self.verbose(f"plot(q={qs},p={ps},'r')")
            plt.plot(qs,ps,'r')
        if self.quantity and self.price:
            plt.plot(self.quantity,self.price,'.k')
        plt.xlabel(f"Quantity ({self.config['quantity_unit']})")
        plt.ylabel(f"Price ({self.config['price_unit']})")
        plt.grid()
        if title:
            if title == 'auto':
                title = f"Auction {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nClears {self.quantity} {self.config['quantity_unit']} at {self.price} {self.config['price_unit']}"
            plt.title(title)
        plt.savefig(filename)

def selftest():

    # create simple auction
    test = auction(price_cap=100.0)

    import random
    q = random.randrange(7,10)
    p = random.randrange(4,20)

    # add some buy orders
    test.add_order(quantity=2,price=1)
    test.add_order(quantity=6,price=30)
    test.add_order(quantity=q-6,price=100)
    test.add_order(quantity=1,price=3)
    test.add_order(quantity=1,price=2)
    ok = False
    try:
        test.add_buy(quantity=1,price=1000)
    except:
        ok = True
    assert(ok)

    # add some sell orders
    test.add_order(quantity=-3,price=0)
    test.add_order(quantity=-3,price=0)
    test.add_order(quantity=-20,price=p)
    
    # clear the market
    test.verbose(f"(q,p) = {(q,p)}")
    result = test.clear()
    assert(result["quantity"] == q and result["price"] == p)
    test.plot(title='selftest')

if __name__ == '__main__':
    selftest()

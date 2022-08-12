from enum import Enum

class OrderType(Enum):
    MARKET = 0
    LIMIT = 1

class Order:

    def __init__(self,agent,quantity,price=None):
        if not type(quantity) is float:
            raise OrderbookError("quantity is not a float")
        self.quantity = float(quantity)
        if type(price) is float:
            self.ordertype = OrderType.LIMIT
            self.price = float(price)
        elif price == None:
            self.ordertype = OrderType.MARKET
            self.price = None
        else:
            raise OrderbookError("price is not a float or None")

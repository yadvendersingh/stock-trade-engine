# This class defines the structure of an order and it acts as a node in the order book
import threading

class Counter:
    def __init__(self):
        self.value = 0

    def next(self):
        self.value += 1
        return self.value

    def get(self):
        return self.value

class Order:
    def __init__(self, order_id, order_type, quantity=0, price=0):
        self.order_id = order_id                #Unique Order ID
        self.matching_order = threading.Event()             #Locking flag to prevent multiple matching of same order
        self.match_counter = Counter()
        self.order_type = order_type            #Type of order (BUY/SELL)
        self.active_quantity = quantity         #Active quantity available to trade
        self.price = price                      #Price of the order
        self.matched_by_orders = []             #List of order IDs that matched this order
        self.settled_quantity = 0               #Quantity settled
        self.total_price = 0                    #Total price of the order
        self.next = None                        #Pointer to next order
        self.prev = None                        #Pointer to previous order
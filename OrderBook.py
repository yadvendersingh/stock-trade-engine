import time
from Order import Order

# This class defines the structure of an order book for a particular ticker
class OrderBook:
    def __init__(self, ticker):
        self.ticker = ticker                                    #Ticker symbol      
        # Head and tail nodes for buy and sell orders to maintain order and ledger
        # Head nodes are used to insert new orders
        # Tail nodes are used to settle orders by moving the settled orders to the tail
        self.buy_orders_head = Order(-1, 'BUY_ORDERS_HEAD')     #Head of buy orders
        self.buy_orders_tail = Order(-1, 'BUY_ORDERS_TAIL')     #Tail of buy orders
        self.sell_orders_head = Order(-1, 'SELL_ORDERS_HEAD')   #Head of sell orders
        self.sell_orders_tail = Order(-1, 'SELL_ORDERS_TAIL')   #Tail of sell orders
        self.buy_orders_head.next = self.buy_orders_tail
        self.buy_orders_tail.prev = self.buy_orders_head
        self.sell_orders_head.next = self.sell_orders_tail
        self.sell_orders_tail.prev = self.sell_orders_head
        self.buy_orders_head.matching_order = True
        self.sell_orders_head.matching_order = True
        self.buy_orders_tail.matching_order = True
        self.sell_orders_tail.matching_order = True

    # Add an order to the order book
    def add_order(self, order):
        if order.order_type == 'BUY':           # BUY order is added at the head of the BUY order list
            head = self.buy_orders_head
        elif order.order_type == 'SELL':        # SELL order list is sorted in ascending order of price to match with BUY orders with lowest price
            head = self.sell_orders_head
            while head.price <= order.price and head.active_quantity > 0:
                head = head.next
        order.next = head.next
        head.next = order
        order.prev = head
        order.next.prev = order

    # Match buy orders with sell orders
    # This function is called in a separate thread for each buy order
    # This function runs in a thread for certain time (timeout) to match the buy order with sell orders
    # If the buy order is not completely settled within the timeout, it is settled with the remaining quantity
    def match_buy_orders(self, order, timeout=2):
        order.matching_order = True
        start_time = time.time()
        
        # Continue matching until the buy order is completely settled or timeout occurs
        while order.active_quantity > 0:
            # Check if timeout has occurred
            if time.time() - start_time > timeout:
                print(f"{self.ticker} {order.order_type} Order {order.order_id} timed out with {order.active_quantity} units unfilled")
                self.settle_order(order)
                break
                
            head = self.sell_orders_head.next
            # Find the first sell order with price less than or equal to the buy order price
            # Continue to the next sell order till the price is less than or equal to the buy order price 
            # and the sell order is active
            while head and head.matching_order and head.price<=order.price and head.active_quantity > 0:
                head = head.next
            # Match the buy order with the sell order if the price is less than or equal to the buy order price
            if head and head.price <= order.price and head.active_quantity > 0:
                head.matching_order = True
                quantity = min(order.active_quantity, head.active_quantity)
                order.active_quantity -= quantity
                order.settled_quantity += quantity
                head.active_quantity -= quantity
                head.settled_quantity += quantity
                order.matched_by_orders.append(head.order_id)
                head.matched_by_orders.append(order.order_id)
                order.total_price += quantity * head.price
                head.total_price += quantity * head.price
                print(f"{self.ticker} {head.order_type} Order {head.order_id} settled by :  {order.order_id}, Quantity traded : {quantity}, Quantity left : {head.active_quantity}" )
                print(f"{self.ticker} {order.order_type} Order {order.order_id} settled by :  {head.order_id}, Quantity traded : {quantity}, Quantity left : {order.active_quantity}" )
                if head.active_quantity == 0:
                    self.settle_order(head)
                if order.active_quantity == 0:
                    self.settle_order(order)
                    head.matching_order = False
                    break
            else:
                # Thread sleep for context switching to other threads in thread pool
                time.sleep(0.01)

    # Settle an order by moving it to the tail of the order list
    def settle_order(self, order):
        if order.order_type == 'BUY':
            order.prev.next = order.next
            order.next.prev = order.prev
            order.next = self.buy_orders_tail
            order.prev = self.buy_orders_tail.prev
            self.buy_orders_tail.prev.next = order
            self.buy_orders_tail.prev = order
        elif order.order_type == 'SELL':
            order.prev.next = order.next
            order.next.prev = order.prev
            order.next = self.sell_orders_tail
            order.prev = self.sell_orders_tail.prev
            self.sell_orders_tail.prev.next = order
            self.sell_orders_tail.prev = order
        order.matching_order = False
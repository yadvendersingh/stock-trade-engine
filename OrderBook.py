import time
from Order import Order

class OrderBook:
    def __init__(self, ticker):
        self.ticker = ticker
        self.buy_orders_head = Order(-1, 'BUY_ORDERS_HEAD')
        self.buy_orders_tail = Order(-1, 'BUY_ORDERS_TAIL')
        self.sell_orders_head = Order(-1, 'SELL_ORDERS_HEAD')
        self.sell_orders_tail = Order(-1, 'SELL_ORDERS_TAIL')

        self.buy_orders_head.next = self.buy_orders_tail
        self.buy_orders_tail.prev = self.buy_orders_head
        self.sell_orders_head.next = self.sell_orders_tail
        self.sell_orders_tail.prev = self.sell_orders_head

        self.buy_orders_head.matching_order.set()
        self.sell_orders_head.matching_order.set()
        self.buy_orders_tail.matching_order.set()
        self.sell_orders_tail.matching_order.set()

    def add_order(self, order):
        if order.order_type == 'BUY':
            current = self.buy_orders_head
            while current.next != self.buy_orders_tail and current.next.price >= order.price:
                current = current.next
        elif order.order_type == 'SELL':
            current = self.sell_orders_head
            while current.next != self.sell_orders_tail and current.next.price <= order.price:
                current = current.next
        else:
            return

        order.next = current.next
        current.next.prev = order
        current.next = order
        order.prev = current

    def match_buy_orders(self, order, timeout=2):
        order.matching_order.set()
        start_time = time.time()

        while order.active_quantity > 0:
            if time.time() - start_time > timeout:
                print(f"[TIMEOUT] {self.ticker} BUY Order {order.order_id} timed out with {order.active_quantity} units unfilled")
                self.settle_order(order)
                break

            head = self.sell_orders_head.next
            while head != self.sell_orders_tail:
                if head.price <= order.price and head.active_quantity > 0 and not head.matching_order.is_set():
                    head.matching_order.set()
                    head.match_counter.next()
                    expected_counter = head.match_counter.get()

                    quantity = min(order.active_quantity, head.active_quantity)

                    new_order_active_quantity = order.active_quantity - quantity
                    new_order_settled_quantity = order.settled_quantity + quantity
                    new_head_active_quantity = head.active_quantity - quantity
                    new_head_settled_quantity = head.settled_quantity + quantity
                    new_order_total_price = order.total_price + quantity * head.price
                    new_head_total_price = head.total_price + quantity * head.price

                    if expected_counter == head.match_counter.get():
                        order.active_quantity = new_order_active_quantity
                        order.settled_quantity = new_order_settled_quantity
                        head.active_quantity = new_head_active_quantity
                        head.settled_quantity = new_head_settled_quantity
                        order.matched_by_orders.append(head.order_id)
                        head.matched_by_orders.append(order.order_id)
                        order.total_price = new_order_total_price
                        head.total_price = new_head_total_price

                        print(f"[MATCH] {self.ticker} SELL {head.order_id} matched with BUY {order.order_id}, qty={quantity}")

                        if head.active_quantity == 0:
                            self.settle_order(head)
                        if order.active_quantity == 0:
                            self.settle_order(order)
                            head.matching_order.clear()
                            break
                    else:
                        head.matching_order.clear()
                        time.sleep(0.001)
                        continue
                head = head.next
            else:
                time.sleep(0.001)

    def settle_order(self, order):
        order.prev.next = order.next
        order.next.prev = order.prev

        if order.order_type == 'BUY':
            order.next = self.buy_orders_tail
            order.prev = self.buy_orders_tail.prev
            self.buy_orders_tail.prev.next = order
            self.buy_orders_tail.prev = order
        elif order.order_type == 'SELL':
            order.next = self.sell_orders_tail
            order.prev = self.sell_orders_tail.prev
            self.sell_orders_tail.prev.next = order
            self.sell_orders_tail.prev = order

        order.matching_order.clear()

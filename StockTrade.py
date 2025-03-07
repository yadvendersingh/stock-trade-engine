import random
import time
from Order import Order
from OrderBook import OrderBook
from concurrent.futures import ThreadPoolExecutor
from StockHashTable import StockHashTable


# Constant value to define limit of tickers
MAX_TICKERS = 10
ORDER_TIMEOUT = 3
NUM_OF_STOCKBROKERS = 10
ORDERS_PER_STOCKBROKER = 10

# Class to simulate stock trade by stockbrokers a list of OrderBook objects for each ticker
# It also contains a global order id generator to assign unique order id to each order
class StockTrade:
    def __init__(self):
        self.order_books = StockHashTable(MAX_TICKERS)                                   # List of OrderBook objects
        self.global_order_id = self._id_generator()             # Global order id to assign unique order id to each order
        self.ticker_symbols = [f"Ticker_{i}" for i in range(1, MAX_TICKERS+1)]
        self.executor = ThreadPoolExecutor(max_workers=20)      # Executor to run threads for matching buy orders with sell orders

    # Function to generate unique order id in a thread-safe manner
    def _id_generator(self):
        i=0
        while True:
            yield i
            i+=1

    # Function to get OrderBook object by ticker from the order_books list
    # If the OrderBook object is not present in the list, it creates a new OrderBook object
    # and appends it to the list
    def get_order_book_by_ticker(self, ticker):
        order_book = self.order_books.get(ticker)
        if order_book is not None:
            return order_book
        order_book = OrderBook(ticker)
        self.order_books.add(ticker, order_book)
        return order_book
        
    # Function to execute an order
    # It creates an Order object and adds it to the OrderBook object
    # It also creates a new thread to match BUY orders with SELL orders in the OrderBook
    def execute_order(self, order_type, ticker, quantity, price):
        book = self.get_order_book_by_ticker(ticker)
        if book is None:
            print("Ticker not found:", ticker)
            return
        
        order_id = next(self.global_order_id)
        order = Order(order_id, order_type, quantity, price)
        print(f"Order {order_id} : {order_type} {ticker} {quantity} {price}")
        book.add_order(order)
        if order_type == 'BUY':
            self.executor.submit(book.match_buy_orders, order, ORDER_TIMEOUT)


    # Function to simulate order execution
    # It generates random orders and executes them to simulate the stock trade by a stockbroker
    # If is_manual is True, it takes input from the user to execute orders (INPUT FORMAT: BUY/SELL ticker quantity price)
    # If is_manual is False, it generates random orders
    def order_simulator(self, num_orders, is_manual=False):
            if is_manual:
                while num_orders > 0:
                    user_input = input("Enter order (format: BUY/SELL ticker quantity price): ")
                    parts = user_input.split()
                    if len(parts) == 4:
                        order_type, ticker, quantity, price = parts
                        quantity = int(quantity)
                        price = float(price)
                        self.execute_order(order_type, ticker, quantity, price)
                        num_orders -= 1
                    else:
                        print("Invalid input format. Using random order instead.")
            else:
                for _ in range(num_orders):
                    order_type = random.choice(['BUY', 'SELL'])
                    ticker = random.choice(self.ticker_symbols)
                    quantity = random.randint(1, 100)
                    price = round(random.uniform(10.0, 1000.0), 2)
                    self.execute_order(order_type, ticker, quantity, price)
                    time.sleep(0.01)
        
    # Function to print the order books
    # It iterates through the order_books list and prints the buy and sell orders in each OrderBook object
    def print_order_books(self):
        print("Order Books:")
        for ticker in self.ticker_symbols:
            book = self.get_order_book_by_ticker(ticker)
            print(f"Ticker: {book.ticker}")
            head = book.buy_orders_head.next
            while head and head.order_id != -1:
                avg_price = round(head.total_price / head.settled_quantity, 2) if head.settled_quantity > 0 else 0
                print(f"Buy Order {head.order_id} : Unsettled Quantity [{head.active_quantity}]; Settled Quantity [{head.settled_quantity}]; Settled By Orders [{head.matched_by_orders}]; Price [{head.price}]; Average Buy Price [{avg_price}]")
                head = head.next
            head = book.sell_orders_head.next
            while head and head.order_id != -1:
                avg_price = round(head.total_price / head.settled_quantity, 2) if head.settled_quantity > 0 else 0
                print(f"Sell Order {head.order_id} : Unsettled Quantity [{head.active_quantity}]; Settled Quantity [{head.settled_quantity}]; Settled By Orders [{head.matched_by_orders}]; Price [{head.price}]; Average Sell Price [{avg_price}]")
                head = head.next

def main():
    stockTrade = StockTrade()
    is_manual = input("Do you want to input orders manually? (y/n): ")
    if is_manual == 'y':
        number_of_stockbrokers = int(input("Enter number of stockbrokers: "))
        orders_per_stockbroker = int(input("Enter number of orders per stockbroker: "))
    else:
        number_of_stockbrokers = NUM_OF_STOCKBROKERS
        orders_per_stockbroker = ORDERS_PER_STOCKBROKER
    executor = ThreadPoolExecutor(max_workers=min(number_of_stockbrokers, 20))
    for _ in range(number_of_stockbrokers):
        executor.submit(stockTrade.order_simulator, orders_per_stockbroker, is_manual=='y')
    #     t = threading.Thread(target=stockTrade.order_simulator, args=(orders_per_stockbroker,is_manual=='y'))
    #     simulator_threads.append(t)
    #     t.start()

    # for t in simulator_threads:
    #     t.join()
    executor.shutdown()
    stockTrade.executor.shutdown()
    stockTrade.print_order_books()
    
if __name__ == '__main__':
    main()

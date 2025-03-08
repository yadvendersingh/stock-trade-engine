# Stock Trade Engine

A simple, multi-threaded stock trading simulation engine that matches buy and sell orders in real-time using a doubly linked list based order book implementation and custom hash table implementation for tickers management.

## Features

- Simulates multiple stock tickers (Number of tickers customizable with `MAX_TICKERS`)
- Real-time matching of buy and sell orders
- Concurrent order processing using thread pools
- Support for both automated and manual order entry
- Order timeout mechanism to handle unmatched BUY orders
- Displays Order Book after completing transactions

## Architecture

The system consists of three main components:

- **Order**: Represents a buy or sell order with quantity, price, and tracking information for matched orders
- **OrderBook**: Maintains buy and sell orders for a specific ticker using doubly linked lists
- **StockTrade**: Coordinates the creation and matching of orders across multiple tickers

## Installation

```bash
# Clone the repository
git clone https://github.com/yadvendersingh/stock-trade-engine.git

# Navigate to project directory
cd stock-trade-engine
```

## Usage

Run the main script to start the simulation:

```bash
python StockTrade.py
```

### Manual Order Entry
When prompted, enter `y` to manually input details 

You will be prompted to enter following details once:
```
Number of Stockbrokers
Orders per Stockbroker
```

Afterwards you will be asked to enter order details in the format:
```
BUY/SELL ticker quantity price
```

For example:
```
Enter order (format: BUY/SELL ticker quantity price): BUY Ticker_1 50 125.50
```
### Order Books HashMap
The custom hashmap is initialized with size of `MAX_TICKERS` and there are functions to add, get and delete order books based on the ticker value

### Automated Simulation
Enter `n` when prompted for manual input to run an automated simulation with random orders.
Number of Stockbrokers and Orders per Stockbroker can be configured for automated simulated by updating constants `NUM_OF_STOCKBROKERS` and `ORDERS_PER_STOCKBROKER` in `StockTrade.py`

## How It Works

1. Automated simulation creates an order book for each stock ticker using `MAX_TICKERS`
2. `BUY` and `SELL` orders are added to their respective linked lists of the OrderBook of given ticker
3. `BUY` orders are the match drivers. For each buy order, a separate thread from thread pool is started that attempts to match it with available sell orders. The time complexity of matching is `O(n)` as the thread linearly scans sell orders linkedlist
4. Matching occurs when a buy order price is greater than or equal to a sell order price
5. Orders can be partially filled, with the remaining quantity stays in the order book
6. After the transactions gets completed, the state of OrderBooks is displayed at the end featuring various statistics such as unsettled quantity, settled quantity, matched order ids, and average buy/sell price

## Order Matching Logic

- Buy orders are matched with the lowest-priced sell orders first
- Partial fills are supported, with the unfilled portion remaining in the order book
- Multiple sell orders can satisfy a single buy order and vice versa
- Orders are settled by moving them to the tail of their respective linked lists

## Future Improvements

- SELL order timeout
- Price charts and visualization
- REST API interface

## License

Apache License
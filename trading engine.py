# -*- coding: utf-8 -*-

# importing modules
import threading 
import random
import time


# class to hold order details

class TickerOrder:
    def __init__(self, order_type, stock_symbol, quantity, price):
        self.order_type = order_type  # "Buy" or "Sell"
        self.ticker = stock_symbol # ticker symbol
        self.quantity = quantity # quantity of stocks
        self.price = price # stock price
        self.timestamp = time.time() # time at which order got placed
        self.matched_quantity = 0 # to store quantity that got matched

# Class that holds transactions creates match order
class StockOrderBook:
    def __init__(self):
        self.buy = []
        self.sell = []
        self.lock = threading.Lock()
        self.history =[]
    
    def insert_order(self, order_list, order, is_buy_order):
        """
        Insert orders in the correct position to maintain sorting:
        - Buy orders: Ticker, Highest price first, Oldest first
        - Sell orders: Ticker, Lowest price first, Oldest first
        """
        left, right = 0, len(order_list)

        while left < right:
            mid = (left + right) // 2
            if is_buy_order:
                # Buy orders: Sorted by (ticker, price DESC, timestamp ASC)
                if (order_list[mid].ticker < order.ticker or
                    (order_list[mid].ticker == order.ticker and order_list[mid].price > order.price) or
                    (order_list[mid].ticker == order.ticker and order_list[mid].price == order.price and order_list[mid].timestamp < order.timestamp)):
                    left = mid + 1
                else:
                    right = mid
            else:
                # Sell orders: Sorted by (ticker, price ASC, timestamp ASC)
                if (order_list[mid].ticker < order.ticker or
                    (order_list[mid].ticker == order.ticker and order_list[mid].price < order.price) or
                    (order_list[mid].ticker == order.ticker and order_list[mid].price == order.price and order_list[mid].timestamp < order.timestamp)):
                    left = mid + 1
                else:
                    right = mid

        order_list.insert(left, order)  # Insert order at the correct position


        
    # function to add Order
    def addOrder(self, order_type, stock_symbol, quantity, price):
        # create order object
        order = TickerOrder(order_type, stock_symbol, quantity, price)
        
        # add order to list based on the type of order
        if order_type == 'Buy':
            self.insert_order(self.buy, order, is_buy_order=True)
        else:
            self.insert_order(self.sell, order, is_buy_order=False)
    
    # match order
    def matchOrder(self):
        # if either of the list is empty return 
        if not self.buy or not self.sell:
            return

        # indices to parse order arrays
        buy_order_index = 0
        sell_order_index = 0
        
        # this loop parses through entire 
        while( buy_order_index < len(self.buy) and sell_order_index < len(self.sell)):
            buy_order = self.buy[buy_order_index]
            sell_order = self.sell[sell_order_index]
            
            if buy_order.ticker == sell_order.ticker:
                if buy_order.price >= sell_order.price:
                    matched_quantity = min(buy_order.quantity, sell_order.quantity)
                    # Adjust quantities and matched quantities
                    buy_order.quantity -= matched_quantity
                    sell_order.quantity -= matched_quantity
                    buy_order.matched_quantity += matched_quantity
                    sell_order.matched_quantity += matched_quantity
                    
                    self.history.append((buy_order.ticker,sell_order.ticker))
                    # Remove fully matched orders
                    if buy_order.quantity == 0:
                        self.buy.pop(buy_order_index) # Move to next Buy order
                    if sell_order.quantity == 0:
                        self.sell.pop(sell_order_index) # Move to next Sell order
                else:
                    buy_order_index +=1
            else:
                if buy_order.ticker < sell_order.ticker:
                    buy_order_index += 1
                else:
                    sell_order_index += 1
        print("Matched: ", self.history)

# Function to simulate adding random orders
def simulate_orders(order_book):
    tickers = [f"STK{i}" for i in range(1, 1025)]  # 1,024 tickers

    while True:
        order_type = random.choice(["Buy", "Sell"])
        ticker = random.choice(tickers)
        quantity = random.randint(1, 100)
        price = random.uniform(10, 500)

        order_book.addOrder(order_type, ticker, quantity, price)
        time.sleep(random.uniform(0.1, 0.5))  # Simulate real-time trading

# Running the order book with multiple threads
if __name__ == "__main__":
    order_book = StockOrderBook()

    # Start multiple threads to add orders
    for _ in range(5):
        threading.Thread(target=simulate_orders, args=(order_book,), daemon=True).start()

    # Match orders every 2 seconds
    while True:
        order_book.matchOrder()
        time.sleep(2)

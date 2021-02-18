import logging
import os
import sys
import time
from typing import List

from binance.client import Client

from messenger import TelegramMessenger, Message
from order_wrappers import DetailedOrder, Order, OrderManager


class BinanceOrderMonitor:

    def __init__(self):
        self.client = Client(
            api_key=os.getenv('API_KEY', 'J7ZuTaZxOhbpMQueXPvS4Q2bO5IKHxlXKsmtAq3wZ63VnGF8kKZGzgt3QlQHhMtI'),
            api_secret=os.getenv('SECRET_KEY', 'lGlIjkbCCEua91jNoN4UQvE8i5WSG5ZoV8h0KCzTHulq9vekE5uq9wFI4XrVD4ee')
        )
        self._messenger = TelegramMessenger()
        self._sleep_interval = int(os.getenv('SLEEP_INTERVAL', 2))

    def get_detailed_open_orders(self) -> List[DetailedOrder]:
        return [DetailedOrder(**order) for order in (self.client.get_open_orders())]

    def get_open_orders_symbols(self) -> List[str]:
        return [order.get_symbol() for order in (self.get_detailed_open_orders())]

    def get_open_orders(self) -> List[Order]:
        return [order.get_order() for order in (self.get_detailed_open_orders())]

    def get_filled_order(self, symbol: str) -> List[DetailedOrder]:
        return [DetailedOrder(**order) for order in (self.client.get_all_orders(symbol=symbol))]

    def is_order_filled(self, order: Order) -> bool:
        return self.get_order(order).is_cancelled

    def get_order(self, order: Order):
        return self.client.get_all_orders(symbol=order.symbol, orderId=order.orderId)

    def start_monitor(self):
        # Starts monitoring for order changes events
        while True:
            try:
                original_orders = self.get_open_orders()
                logging.info(f'Original Orders: {original_orders}')
                time.sleep(self._sleep_interval)

                updated_orders = self.get_open_orders()
                logging.info(f'Updated Orders: {updated_orders}')

                orders_added, orders_removed = OrderManager.identify_order_changes(original_orders=original_orders,
                                                                                   new_orders=updated_orders)

                # Check if order is cancelled or filled
                for order in orders_removed:
                    if self.is_order_filled(order):
                        logging.info(f'Order {order} has been filled')
                        self._messenger.send_message(
                            message=Message(f'Order #{order.orderId}, {order.symbol} has been filled'))

            except KeyboardInterrupt:
                logging.error(f"Interrupted: {sys.exc_info()[0]}")
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)

            except Exception as e:
                if hasattr(e, 'message'):
                    logging.error(f"Fatal Error: {e.message}")
                logging.error(f"Fatal Error: {sys.exc_info()[0]}")

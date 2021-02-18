import logging
import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from binance.client import Client

from messenger import TelegramMessenger, Message
from order_wrappers import DetailedOrder, Order


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

    def get_last_order(self, symbol: str) -> DetailedOrder:
        order = [DetailedOrder(**order) for order in (self.client.get_all_orders(symbol=symbol, limit=1))]
        return order[0]

    def is_last_order_filled(self, symbol: str) -> bool:
        return self.get_last_order(symbol).is_cancelled

    def get_order_by_id(self, id: int):
        return self.client.get_all_orders(orderId=id)

    def start_monitor(self):
        # Starts monitoring for order changes events
        while True:
            try:
                orders = self.get_open_orders()
                time.sleep(self._sleep_interval)
                new_order = self.get_open_orders()

                missing_orders, new_orders = set(order_ids) - set(new_order_ids)

                # Check if order is cancelled or filled
                for order in missing_orders:
                    if self.is_last_order_filled(order_id):
                        # TODO build better message
                        self._messenger.send_message(message=Message(f'Order {symbol} has been filled'))

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


if __name__ == '__main__':
    client = BinanceOrderMonitor()
    # s = client.is_last_order_filled(symbol='REEFUSDT')
    s = client.get_order_by_id(34154801)
    print(s)

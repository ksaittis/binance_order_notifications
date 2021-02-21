import logging
import os
import sys
import time

from messenger import TelegramMessenger, Message, MessageBuilder
from order_wrappers import OrderEvaluator, OrderManager


class BinanceOrderMonitor:

    def __init__(self):
        self._order_manager = OrderManager()
        self._messenger = TelegramMessenger()
        self._sleep_interval = int(os.getenv('SLEEP_INTERVAL', 2))

    def start_monitor(self):
        # Starts monitoring for order changes events
        while True:
            try:
                original_orders = self._order_manager.get_open_orders()
                logging.info(f'Original Orders: {original_orders}')

                time.sleep(self._sleep_interval)

                updated_orders = self._order_manager.get_open_orders()
                #  Next line just for testing
                # updated_orders.pop(0)

                logging.info(f'Updated Orders: {updated_orders}')

                orders_removed, orders_added = OrderEvaluator.identify_order_changes(original_orders=original_orders,
                                                                                     new_orders=updated_orders)

                # Check if order is cancelled or filled
                for order in orders_removed:
                    detailed_order = self._order_manager.get_order(order)
                    # if detailed_order.is_new:
                    if detailed_order.is_filled:
                        logging.info(
                            f'Order {detailed_order.get_symbol()}, changed status to {detailed_order.get_status()}')
                        self._messenger.send_message(message=MessageBuilder.build_msg(detailed_order))

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

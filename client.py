import logging
import os
import sys
import time

from messenger import TelegramMessenger, MessageBuilder
from order_wrappers import OrderEvaluator, OrderManager


class BinanceOrderMonitor:

    def __init__(self):
        self._order_manager = OrderManager()
        self._messenger = TelegramMessenger()
        self._sleep_interval = int(os.getenv('SLEEP_INTERVAL', 2))

    def start_monitor(self):
        # Starts monitoring for order changes events
        original_orders = self._order_manager.get_open_orders()
        while True:
            try:
                logging.info(f'Original Orders Identified: {original_orders}')
                time.sleep(self._sleep_interval)

                updated_orders = self._order_manager.get_open_orders()

                if OrderEvaluator.have_orders_changed(original_orders, updated_orders):
                    logging.info('Identified order changes')

                    orders_removed, orders_added = OrderEvaluator.identify_order_changes(
                        original_orders=original_orders,
                        new_orders=updated_orders)

                    # Update original orders
                    original_orders = updated_orders

                    logging.info(f'Missing orders {orders_removed}')
                    logging.info(f'New orders {orders_added}')

                    # Missing Orders, can be either filled or cancelled
                    for order in orders_removed:
                        detailed_order = self._order_manager.get_order(order)

                        if detailed_order.is_filled:
                            logging.info(
                                f'Order {detailed_order.get_symbol()}, changed status to {detailed_order.get_status()}')
                            self._messenger.send_message(message=MessageBuilder.build_msg(detailed_order))

                        elif detailed_order.is_cancelled:
                            logging.info(
                                f'Order {detailed_order.get_symbol()}, changed status to {detailed_order.get_status()}')
                            self._messenger.send_message(message=MessageBuilder.build_msg(detailed_order))

                    # New Orders
                    for order in orders_added:
                        detailed_order = self._order_manager.get_order(order)
                        if detailed_order.is_new:
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

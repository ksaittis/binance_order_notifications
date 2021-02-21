import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple

from binance.client import Client


class OrderStatus(Enum):
    ACTIVE = 'active'
    FILLED = 'filled'
    CANCELED = 'canceled'
    NEW = 'new'


@dataclass
class Order:
    symbol: str
    orderId: int

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other):
        return self.orderId < other.orderId

    def __repr__(self):
        return f'Order({self.symbol}, {self.orderId})'

    def __eq__(self, other):
        if not isinstance(other, Order):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.symbol == other.symbol and self.orderId == other.orderId


class OrderEvaluator:
    @staticmethod
    def get_missing_orders(original_orders: List[Order], new_orders: List[Order]) -> List[Order]:
        return list(set(original_orders) - set(new_orders))

    @staticmethod
    def get_new_orders(original_orders: List[Order], new_orders: List[Order]) -> List[Order]:
        return list(set(new_orders) - set(original_orders))

    @staticmethod
    def identify_order_changes(original_orders: List[Order],
                               new_orders: List[Order]) -> Tuple[List[Order], List[Order]]:
        orders_added = OrderEvaluator.get_new_orders(original_orders, new_orders)
        orders_removed = OrderEvaluator.get_missing_orders(original_orders, new_orders)

        return orders_removed, orders_added


class DetailedOrder:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def get_order(self) -> Order:
        return Order(symbol=self.get_symbol(), orderId=self.get_id())

    def get_symbol(self) -> Optional[str]:
        if 'symbol' in self.__dict__:
            return self.symbol
        return None

    def get_id(self) -> int:
        if 'orderId' in self.__dict__:
            return self.orderId
        return -1

    @property
    def total(self) -> float:
        return self.get_price() * float(self.origQty)

    def get_price(self) -> float:
        return float(self.price)

    def get_status(self) -> Optional[str]:
        if 'status' in self.__dict__:
            return self.status.lower()
        return None

    @property
    def is_filled(self) -> bool:
        return self.get_status() == OrderStatus.FILLED.value

    @property
    def is_active(self) -> bool:
        return self.get_status() == OrderStatus.ACTIVE.value

    @property
    def is_cancelled(self) -> bool:
        return self.get_status() == OrderStatus.CANCELED.value

    @property
    def is_new(self) -> bool:
        return self.get_status() == OrderStatus.NEW.value


class OrderManager:
    def __init__(self):
        self.client = Client(
            api_key=os.getenv('API_KEY', 'J7ZuTaZxOhbpMQueXPvS4Q2bO5IKHxlXKsmtAq3wZ63VnGF8kKZGzgt3QlQHhMtI'),
            api_secret=os.getenv('SECRET_KEY', 'lGlIjkbCCEua91jNoN4UQvE8i5WSG5ZoV8h0KCzTHulq9vekE5uq9wFI4XrVD4ee')
        )

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

    def get_order(self, order: Order) -> DetailedOrder:
        order = self.client.get_all_orders(symbol=order.symbol, orderId=order.orderId)[0]
        return DetailedOrder(**order)

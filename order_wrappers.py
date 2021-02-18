from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple


class OrderStatus(Enum):
    ACTIVE = 'active'
    FILED = 'filled'
    CANCELED = 'canceled'
    NEW = 'new'


@dataclass
class Order:
    symbol: str
    orderId: int

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, Order):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.symbol == other.symbol and self.orderId == other.orderId


class OrderManager:
    @staticmethod
    def get_missing_orders(original_orders: List[Order], new_orders: List[Order]) -> List[Order]:
        return list(set(original_orders) - set(new_orders))

    @staticmethod
    def get_new_orders(original_orders: List[Order], new_orders: List[Order]) -> List[Order]:
        return list(set(new_orders) - set(original_orders))

    @staticmethod
    def identify_order_changes(original_orders: List[Order],
                               new_orders: List[Order]) -> Tuple[List[Order], List[Order]]:
        new_orders = OrderManager.get_new_orders(original_orders, new_orders)
        missing_orders = OrderManager.get_missing_orders(original_orders, new_orders)

        return missing_orders, new_orders


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

    def get_status(self) -> Optional[str]:
        if 'status' in self.__dict__:
            return self.status.lower()
        return None

    @property
    def is_filled(self) -> bool:
        return self.get_status() == OrderStatus.FILED.value

    @property
    def is_active(self) -> bool:
        return self.get_status() == OrderStatus.ACTIVE.value

    @property
    def is_cancelled(self) -> bool:
        return self.get_status() == OrderStatus.CANCELED.value

    @property
    def is_new(self) -> bool:
        return self.get_status() == OrderStatus.NEW.value

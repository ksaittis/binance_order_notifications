import unittest
from typing import List

from order_wrappers import Order, OrderManager


class TestOrders(unittest.TestCase):

    def test_diff_order(self):
        # Given
        order1 = Order(symbol="BTCGBP", orderId=1)
        order2 = Order(symbol="1INCHUSDT", orderId=2)

        self.assertTrue(order1 != order2)

    def test_same_order(self):
        # Given
        order1 = Order(symbol="BTCGBP", orderId=1)
        order2 = Order(symbol="BTCGBP", orderId=1)

        self.assertTrue(order1 == order2)

    def test_same_orders(self):
        # Given
        orders1 = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2)]
        orders2 = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2)]

        self.assertTrue(orders1 == orders2)

    def test_diff_orders(self):
        # Given
        orders1 = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2)]
        orders2 = [Order(symbol="BTCGBP", orderId=1), Order(symbol="ETHUSDT", orderId=2)]

        self.assertTrue(orders1 != orders2)

    def test_identify_missing_orders(self):
        # Given
        expected_missing_order = Order(symbol="1INCHUSDT", orderId=2)
        original_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1), expected_missing_order]
        new_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1)]

        # When
        missing_order = OrderManager.get_missing_orders(original_orders, new_orders)

        # Then
        self.assertTrue(missing_order[0] == expected_missing_order)

    def test_identify_new_orders(self):
        # Given
        expected_new_order = Order(symbol="ETHGBP", orderId=2)
        original_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2)]
        new_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2),
                                   expected_new_order]

        # When
        new_order = OrderManager.get_new_orders(original_orders, new_orders)

        # Then
        self.assertTrue(new_order[0] == expected_new_order)

    def test_identify_single_missing_order_multiple_new(self):
        # Given
        expected_missing_order = Order(symbol="1INCHUSDT", orderId=2)
        original_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1),
                                        expected_missing_order]
        new_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1),
                                   Order(symbol="ETHGBP", orderId=1),
                                   Order(symbol="ADAGBP", orderId=1)]

        # When
        missing_order = OrderManager.get_missing_orders(original_orders, new_orders)

        # Then
        self.assertTrue(missing_order[0] == expected_missing_order)

    def test_identify_multiple_new_orders(self):
        # Given
        expected_new_order = Order(symbol="ETHGBP", orderId=2)
        expected_new_order2 = Order(symbol="ADAGBP", orderId=5)
        original_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2)]
        new_orders: List[Order] = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2),
                                   expected_new_order, expected_new_order2]

        # When
        new_order = OrderManager.get_new_orders(original_orders, new_orders)

        # Then
        self.assertTrue(new_order == [expected_new_order2, expected_new_order])

    def test_identify_missing_and_new_orders(self):
        # Given
        expected_missing_orders = [Order(symbol="BTCGBP", orderId=1), Order(symbol="1INCHUSDT", orderId=2)]
        expected_new_orders = [Order(symbol="VETGBP", orderId=3), Order(symbol="ADABTC", orderId=4)]

        original_orders = [Order(symbol="DOTUSDT", orderId=6), Order(symbol="CHAINBTC", orderId=5)]
        original_orders.extend(expected_missing_orders)

        new_orders = [Order(symbol="DOTUSDT", orderId=6), Order(symbol="CHAINBTC", orderId=5)]
        new_orders.extend(expected_new_orders)

        # When
        actual_missing_orders, actual_new_orders = OrderManager.identify_order_changes(original_orders, new_orders)

        # Then
        self.assertTrue(actual_missing_orders == expected_missing_orders)
        self.assertTrue(actual_new_orders == expected_new_orders)


if __name__ == '__main__':
    unittest.main()

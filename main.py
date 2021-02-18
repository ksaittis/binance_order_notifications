from client import BinanceOrderMonitor

if __name__ == '__main__':
    order_monitor = BinanceOrderMonitor()
    order_monitor.start_monitor()

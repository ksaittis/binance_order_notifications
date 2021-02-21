import os
from dataclasses import dataclass

import requests
import logging

from order_wrappers import DetailedOrder


@dataclass
class Message:
    text: str


class MessageBuilder:
    @staticmethod
    def build_msg(detailed_order: DetailedOrder) -> Message:
        return Message(
            text=f'{detailed_order.type.capitalize()} {detailed_order.side} order {detailed_order.symbol} '
                 f'has been {detailed_order.get_status()}, price {detailed_order.get_price()}, '
                 f'qty {detailed_order.origQty} for a total {detailed_order.total}')


class TelegramMessenger:
    BASE_ENDPOINT = 'https://api.telegram.org/bot'
    CHANNEL_ID = os.getenv('CHANNEL_ID', '1573650489')
    BOT_CHAT_ID = '1573650489'
    USER_CHAT_ID = '-493956374'

    def __init__(self):
        self.bot_token = os.getenv('ORDER_NOTIFICATIONS_BOT_TOKEN', '1662096681:AAHrrqdEHsQXx3IerCxNWHdhkF4Lh6jXfb8')
        self.chat_id = os.getenv('CHAT_ID', '1573650489')

    def send_message(self, message: Message):
        telegram_send_message_endpoint = self.build_message_endpoint(message)
        response = requests.get(telegram_send_message_endpoint)
        if response.ok:
            logging.info(f"Message delivery successful: {response.status_code} {message.text}")
        else:
            logging.warning(f"Message delivery unsuccessful: {response.status_code} {message.text}")

    def build_message_endpoint(self, message: Message):
        return f'https://api.telegram.org/bot{self.bot_token}/sendMessage?' \
               f'chat_id={self.chat_id}' \
               f'&parse_mode=Markdown' \
               f'&text={message.text}'


if __name__ == '__main__':
    m = TelegramMessenger()
    m.send_message(Message('test teststtststsssssssssssssssssssssssss'))

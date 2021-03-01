import os
from dataclasses import dataclass
from enum import Enum

import requests
import logging

from order_wrappers import DetailedOrder


class Emoji(Enum):
    GREEN_SQUARE = '\U0001F7E9'
    RED_SQUARE = '\U0001F7E5'
    STAR = '\U00002B50'
    STOP_SIGN = '\U0001F6D1'
    NEW = '\U0001F195'
    RECYCLE = '\U0000267B'
    MONEY = '\U0001F4B0'
    CONFUSED = '\U0001F615'


@dataclass
class Message:
    text: str


class MessageBuilder:
    @staticmethod
    def _get_msg_prefix_emoji(order_side: str) -> Emoji:
        if order_side.lower() == 'buy':
            return Emoji.RED_SQUARE
        elif order_side.lower() == 'sell':
            return Emoji.GREEN_SQUARE
        elif order_side.lower() == 'cancel':
            return Emoji.RECYCLE
        return Emoji.STOP_SIGN

    @staticmethod
    def _get_symbol_formatted(symbol: str) -> str:
        if len(symbol) == 8:
            return f'{symbol[:4]}/{symbol[4:]}'
        elif len(symbol) == 6:
            return f'{symbol[:3]}/{symbol[3:]}'
        elif len(symbol) == 7:
            return f'{symbol[:3]}/{symbol[4:]}'
        return symbol

    @staticmethod
    def build_msg(detailed_order: DetailedOrder) -> Message:
        emoji_prefix: Emoji = MessageBuilder._get_msg_prefix_emoji(detailed_order.side)
        formatted_symbol = MessageBuilder._get_symbol_formatted(detailed_order.get_symbol())

        return Message(
            text=f'{emoji_prefix.value} {formatted_symbol} {detailed_order.side.upper()} {detailed_order.get_status()}, '
                 f'{detailed_order.get_price()}*{detailed_order.origQty}={detailed_order.total} {Emoji.MONEY.value}')


class TelegramMessenger:
    BASE_ENDPOINT = 'https://api.telegram.org/bot'

    def __init__(self):
        self.bot_token = os.getenv('ORDER_NOTIFICATIONS_BOT_TOKEN', '1649540746:AAHvVA3D_s8mzXDj2vbCmaTCcYWsdC1gGxo')
        self.chat_id = os.getenv('CHAT_ID', '-1001478516526')

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
    m.send_message(Message('test'))

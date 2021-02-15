import os
from dataclasses import dataclass

import requests
import logging


@dataclass
class Message:
    text: str
    chat_id: str = None


class TelegramMessenger:
    BASE_ENDPOINT = 'https://api.telegram.org/bot'
    CHANNEL_ID = os.getenv('CHANNEL_ID', '-1001399746625')
    BOT_CHAT_ID = '1573650489'
    USER_CHAT_ID = '-493956374'

    def __init__(self):
        self.bot_token = os.getenv('ORDER_NOTIFICATIONS_BOT_TOKEN', '1662096681:AAHrrqdEHsQXx3IerCxNWHdhkF4Lh6jXfb8')

    def send_message(self, message: Message, disable_notification: bool):
        telegram_send_message_endpoint = self.build_message_endpoint(message, disable_notification)
        response = requests.get(telegram_send_message_endpoint)
        if response.ok:
            logging.info(f"Message delivery successful: {response.status_code} {message.text}")
        else:
            logging.warning(f"Message delivery unsuccessful: {response.status_code} {message.text}")

    def build_message_endpoint(self, message: Message, disable_notification: bool):
        return f'https://api.telegram.org/bot{self.bot_token}/sendMessage?' \
               f'chat_id={message.chat_id}' \
               f'&text={message.text}' \
               f'&disable_web_page_preview=true'

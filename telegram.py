import os

import requests


def send_message(chat_id, message, token, is_error=False):
    # TODO: send errors to a special chat
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    response = requests.get(url)
    return response.status_code

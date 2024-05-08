import os
import requests


TG_TOKEN = os.getenv("TG_TOKEN")


def send_message(chat_id, message, is_error=False):
    # TODO: send errors to a special chat
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    response = requests.get(url)
    return response.status_code

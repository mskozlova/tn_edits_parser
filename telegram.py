import requests


def send_message(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    return requests.get(url).json()

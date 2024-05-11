import os
import requests
import time

TECH_CHAT_ID = os.getenv("TECH_CHAT_ID")


def send_messages(user_chat_id, status, token, sleep_s):
    user_message, technical_message = status.get_messages()
    user_status_code = 200
    
    if user_message is not None:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={user_chat_id}&text={user_message}"
        response = requests.get(url)
        user_status_code = response.status_code
        
    time.sleep(sleep_s)
        
    if technical_message is not None:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={TECH_CHAT_ID}&text={technical_message}"
        requests.get(url)

    return user_status_code

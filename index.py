import os
import time

from database.ydb_settings import get_ydb_pool
from database import model as db_model
from logs import logger
import telegram
import tn_parser


TN_USER_ID = os.getenv("TN_USER_ID")
TN_COOKIE = os.getenv("TN_COOKIE")

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = int(os.getenv("TG_CHAT_ID"))

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")


def handler(event, context):
    logger.debug("Started execution")
    
    pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)
    
    do_send = False
    
    prev_last_edited = db_model.get_last_edited(pool, chat_id=TG_CHAT_ID)
    prev_error_timestamp = db_model.get_error_info(pool, chat_id=TG_CHAT_ID)
    
    try:
        html = tn_parser.get_html(user_id=TN_USER_ID, cookie=TN_COOKIE)
        message = tn_parser.parse_last_edited(html)

        if prev_last_edited is None or prev_last_edited != message:
            do_send = True
            db_model.set_last_edited(pool, chat_id=TG_CHAT_ID, last_edited=message)

        if prev_error_timestamp is not None:
            if not do_send:
                message = "Error resolved!"
                do_send = True
            else:
                message += " (Error resolved!)"
            db_model.reset_error_info(pool, chat_id=TG_CHAT_ID)

    except Exception as e:
        message = str(e)
        if prev_error_timestamp is None:
            do_send = True
            db_model.set_error_info(pool, chat_id=TG_CHAT_ID, error_timestamp=int(time.time()))
        
    logger.debug(f"Message: {message}, do send: {do_send}")
    
    if do_send:
        telegram.send_message(message=message, token=TG_TOKEN, chat_id=TG_CHAT_ID)
    
    logger.debug("Finished execution")
    
    return {
        'statusCode': 200,
        'body': '!',
    }

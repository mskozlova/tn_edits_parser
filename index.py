import os
import time

from database.ydb_settings import get_ydb_pool
from logs import logger
from telegram import send_message
from tracker import get_updates


YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")


def handler(event, context):
    logger.debug("Started execution")
    
    pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)
    updates = get_updates(pool)
    
    logger.debug(f"Updates: {list(map(str, updates))}")
    
    for update in updates:
        send_message(chat_id=update.chat_id, message=update.message)
        time.sleep(0.5)
    
    logger.debug("Finished execution")
    
    return {
        'statusCode': 200,
        'body': '!',
    }

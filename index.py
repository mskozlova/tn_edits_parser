import os
import time

from database.ydb_settings import get_ydb_pool
from logs import logger
from telegram import send_message
from tracker import get_updates, save_updates

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")


def handler(event, context):
    logger.debug("Started execution")

    pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)
    updates = get_updates(pool)

    logger.debug(f"Updates: {list(map(str, updates))}")

    notified_updates = []
    for update in updates:
        status_code = send_message(
            chat_id=update.db_entry["chat_id"], message=update.message
        )
        if status_code == 200:
            notified_updates.append(update)
        time.sleep(0.5)

    save_updates(pool, notified_updates)

    logger.debug("Finished execution")

    return {
        "statusCode": 200,
        "body": "!",
    }

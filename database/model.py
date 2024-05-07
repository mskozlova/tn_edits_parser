import json

from database import queries
from database.utils import execute_select_query, execute_update_query


def get_last_edited(pool, chat_id):
    results = execute_select_query(pool, queries.get_last_edited, chat_id=chat_id)
    if len(results) == 0:
        return None
    return json.loads(results[0]["last_edited"])


def set_last_edited(pool, chat_id, last_edited):
    execute_update_query(
        pool, queries.set_last_edited, chat_id=chat_id, last_edited=json.dumps(last_edited)
    )


def get_error_info(pool, chat_id):
    results = execute_select_query(pool, queries.get_error_info, chat_id=chat_id)
    if len(results) == 0:
        return None
    return results[0]["error_timestamp"]


def set_error_info(pool, chat_id, error_timestamp):
    execute_update_query(
        pool, queries.set_error_info, chat_id=chat_id, error_timestamp=error_timestamp
    )


def reset_error_info(pool, chat_id):
    execute_update_query(pool, queries.reset_error_info, chat_id=chat_id)
    

def get_tracker_info(pool):
    results = execute_select_query(pool, queries.get_tracker_info)
    return results

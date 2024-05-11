import json

from database import queries
from database.utils import execute_select_query, execute_update_query


def get_tracker_info(pool):
    results = execute_select_query(pool, queries.get_tracker_info)
    return results


def update_tracker_info(pool, db_entries):
    execute_update_query(
        pool,
        queries.update_tracker_info,
        chat_ids=[e.db_entry["chat_id"] for e in db_entries],
        emails=[e.db_entry["email"] for e in db_entries],
        last_reference_ids=[e.db_entry["last_reference_id"] for e in db_entries],
        last_editeds=[e.db_entry["last_edited"] for e in db_entries],
        last_error_timestamps=[e.db_entry["last_error_timestamp"] for e in db_entries],
        last_updated_timestamps=[e.db_entry["last_updated_timestamp"] for e in db_entries],
    )


def add_tracking(pool, chat_id, email, password, last_updated_timestamp):
    execute_update_query(
        pool, queries.add_tracking, chat_id=chat_id, email=email, password=password, last_updated_timestamp=last_updated_timestamp
    )


def get_chat_trackings(pool, chat_id):
    results = execute_select_query(pool, queries.get_chat_trackings, chat_id=chat_id)
    return [result["email"] for result in results]


def delete_tracking(pool, chat_id, email):
    execute_update_query(pool, queries.delete_tracking, chat_id=chat_id, email=email)


def get_state(pool, chat_id):
    results = execute_select_query(pool, queries.get_user_state, chat_id=chat_id)
    if len(results) == 0:
        return None
    if results[0]["state"] is None:
        return None
    return json.loads(results[0]["state"])


def set_state(pool, chat_id, state):
    execute_update_query(
        pool, queries.set_user_state, chat_id=chat_id, state=json.dumps(state)
    )


def clear_state(pool, chat_id):
    execute_update_query(pool, queries.set_user_state, chat_id=chat_id, state=None)

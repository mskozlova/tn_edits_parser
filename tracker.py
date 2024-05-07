from database import model as db_model
from tn_parser import get_last_application


class Update:
    def __init__(self, chat_id, message):
        self.chat_id = chat_id
        self.message = message
        
    def __str__(self):
        return f"Chat ID: {self.chat_id}, message: {self.message}"


def get_updates(ydb_pool):
    updates = []
    tracked_accounts = db_model.get_tracker_info(ydb_pool)

    for entry in tracked_accounts:
        application = get_last_application(entry["email"], entry["password"])
        updates.append(Update(entry["chat_id"], application.last_edited_ts))
        
    return updates


    # do_send = False
    
    # prev_last_edited = db_model.get_last_edited(pool, chat_id=TG_CHAT_ID)
    # prev_error_timestamp = db_model.get_error_info(pool, chat_id=TG_CHAT_ID)
    
    # try:
    #     html = tn_parser.get_html(user_id=TN_USER_ID, cookie=TN_COOKIE)
    #     message = tn_parser.parse_last_edited(html)

    #     if prev_last_edited is None or prev_last_edited != message:
    #         do_send = True
    #         db_model.set_last_edited(pool, chat_id=TG_CHAT_ID, last_edited=message)

    #     if prev_error_timestamp is not None:
    #         if not do_send:
    #             message = "Error resolved!"
    #             do_send = True
    #         else:
    #             message += " (Error resolved!)"
    #         db_model.reset_error_info(pool, chat_id=TG_CHAT_ID)

    # except Exception as e:
    #     message = str(e)
    #     if prev_error_timestamp is None:
    #         do_send = True
    #         db_model.set_error_info(pool, chat_id=TG_CHAT_ID, error_timestamp=int(time.time()))
        
    # logger.debug(f"Message: {message}, do send: {do_send}")
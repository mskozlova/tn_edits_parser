import time
import traceback

from database import model as db_model
from logs import logger
from tn_parser import get_last_application

UPDATES_LIMIT = 10


class Status:
    def __init__(self, db_entry):
        logger.debug(
            f"Created status. Chat ID: {db_entry['chat_id']}, email: {db_entry['email']}",
            extra={"DB entry": db_entry}
        )
        self.db_entry = db_entry
        self.application = None
        self.exception = None
        self.tags = []

    def load_application(self):
        try:
            self.application = get_last_application(
                self.db_entry["email"], self.db_entry["password"]
            )
            logger.debug(
                f"Loaded application. Chat ID: {self.db_entry['chat_id']}, email: {self.db_entry['email']}",
                extra={"DB entry": self.db_entry, "Application": self.application}
            )
        except Exception as e:
            logger.error(
                f"Error while loading the application. "
                + f"Chat ID: {self.db_entry['chat_id']}, email: {self.db_entry['email']}. "
                + f"Exception: {e}",
                extra={
                    "chat_id": self.db_entry["chat_id"],
                    "email": self.db_entry["email"],
                    "error": e,
                    "traceback": traceback.format_exc(),
                },
            )
            self.exception = e

    def process(self):
        logger.debug(
            f"Processing status. Chat ID: {self.db_entry['chat_id']}, email: {self.db_entry['email']}",
            extra={"DB entry": self.db_entry, "Application": self.application}
        )
        
        if self.exception is not None:
            if self.db_entry["last_error_timestamp"] is None:
                self.db_entry["last_error_timestamp"] = int(time.time())
                self.tags.append("ERROR")

        elif (
            self.db_entry["last_edited"] is None
            and self.application.last_edited_ts is not None
        ):
            if self.db_entry["last_error_timestamp"] is not None:
                self.tags.append("RESOLVED ERROR")
            
            self.db_entry["last_edited"] = self.application.last_edited_ts
            self.db_entry["last_reference_id"] = self.application.reference_id
            self.db_entry["last_error_timestamp"] = None
            self.tags.append("FIRST EDIT")

        elif (
            self.application.last_edited_ts is not None
            and self.application.last_edited_ts != self.db_entry["last_edited"]
        ):
            if self.db_entry["last_error_timestamp"] is not None:
                self.tags.append("RESOLVED ERROR")
            
            self.db_entry["last_edited"] = self.application.last_edited_ts
            self.db_entry["last_reference_id"] = self.application.reference_id
            self.db_entry["last_error_timestamp"] = None
            self.tags.append("NEW EDIT")

        elif self.db_entry["last_error_timestamp"] is not None:
            self.tags.append("RESOLVED ERROR")
            self.db_entry["last_error_timestamp"] = None
        
        logger.debug(
            f"Processing status DONE. Chat ID: {self.db_entry['chat_id']}, email: {self.db_entry['email']}",
            extra={
                "Final DB entry": self.db_entry,
                "Application": self.application,
                "Tags": self.tags,
                "Exception": self.exception,
            }
        )     
        return len(self.tags) > 0
    
    def get_messages(self):
        user_message = None
        technical_message = None
        
        if "FIRST EDIT" in self.tags:
            user_message = (
                f"🏁 First edit registered\n{self.application.name}\n{self.db_entry['email']}\n"
                f"Reference ID: {self.application.reference_id}\n"
                f"Submitted on: {self.application.submitted_ts}\n\n"
                f"Last edited: {self.application.last_edited_ts}"
            )
        elif "NEW EDIT" in self.tags:
            user_message = (
                f"🎉 New edit!\n{self.application.name}\n{self.db_entry['email']}\n"
                f"Reference ID: {self.application.reference_id}\n"
                f"Submitted on: {self.application.submitted_ts}\n\n"
                f"Last edited: {self.application.last_edited_ts}",
            )
            
        if "ERROR" in self.tags:
            technical_message = f"💔 An error occured\n{self.db_entry['email']}\n{self.exception}"
        elif "RESOLVED ERROR" in self.tags:
            technical_message = f"❤️‍🩹 Error resolved\n{self.db_entry['email']}"
        
        logger.debug(
            f"Messages created. Chat ID: {self.db_entry['chat_id']}, email: {self.db_entry['email']}",
            extra={
                "Final DB entry": self.db_entry,
                "Application": self.application,
                "Tags": self.tags,
                "Exception": self.exception,
                "User Message": user_message,
                "Technical Message": technical_message,
            }
        )     
        return user_message, technical_message


def get_updates(ydb_pool):
    updates = []
    tracked_accounts = db_model.get_tracker_info(ydb_pool)

    for entry in tracked_accounts:
        status = Status(entry)
        status.load_application()
        is_update = status.process()
        if is_update:
            updates.append(status)

    # making sure that Yandex Cloud Function does not timeout
    # it's okay to send edit updates a little later - during the next Function run
    logger.debug(f"Found {len(updates)} updates. Truncating down to {UPDATES_LIMIT}.")
    return updates[:UPDATES_LIMIT]


def save_updates(ydb_pool, updates):
    db_model.update_tracker_info(ydb_pool, updates)

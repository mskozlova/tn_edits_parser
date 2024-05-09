import time
import traceback

from database import model as db_model
from logs import logger
from tn_parser import get_last_application

UPDATES_LIMIT = 10


class Update:
    def __init__(self, db_entry, message):
        self.db_entry = db_entry
        self.message = message


class Status:
    def __init__(self, db_entry):
        self.db_entry = db_entry
        self.application = None
        self.exception = None

    def load_application(self):
        try:
            self.application = get_last_application(
                self.db_entry["email"], self.db_entry["password"]
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
        if self.exception is not None:
            if self.db_entry["last_error_timestamp"] is None:
                self.db_entry["last_error_timestamp"] = int(time.time())
                return True, True, Update(
                    self.db_entry,
                    f"💔 An error occured\n{self.db_entry['email']}\n{self.exception}",
                )
            return False, True, None

        if (
            self.db_entry["last_edited"] is None
            and self.application.last_edited_ts is not None
        ):
            self.db_entry["last_edited"] = self.application.last_edited_ts
            self.db_entry["last_reference_id"] = self.application.reference_id
            self.db_entry["last_error_timestamp"] = None
            return (
                True,
                False,
                Update(
                    self.db_entry,
                    f"🏁 First edit registered\n{self.application.name}\n{self.db_entry['email']}\n"
                    + f"Reference ID: {self.application.reference_id}\n"
                    + f"Submitted on: {self.application.submitted_ts}\n\n"
                    f"Last edited: {self.application.last_edited_ts}",
                ),
            )

        if (
            self.application.last_edited_ts is not None
            and self.application.last_edited_ts != self.db_entry["last_edited"]
        ):
            self.db_entry["last_edited"] = self.application.last_edited_ts
            self.db_entry["last_reference_id"] = self.application.last_reference_id
            self.db_entry["last_error_timestamp"] = None
            return (
                True,
                False,
                Update(
                    self.db_entry,
                    f"🎉 New edit!\n{self.application.name}\n{self.db_entry['email']}\n"
                    + f"Reference ID: {self.application.reference_id}\n"
                    + f"Submitted on: {self.application.submitted_ts}\n\n"
                    f"Last edited: {self.application.last_edited_ts}",
                ),
            )
            
        if self.db_entry["last_error_timestamp"] is not None:
            self.db_entry["last_error_timestamp"] = None
            return (
                True,
                True,
                Update(
                    self.db_entry,
                    f"❤️‍🩹 Error resolved\n{self.db_entry['email']}\nNo edit updates.",
                ),
            )

        return False, False, None


def get_updates(ydb_pool):
    updates = []
    tracked_accounts = db_model.get_tracker_info(ydb_pool)

    for entry in tracked_accounts:
        status = Status(entry)
        status.load_application()
        do_send, is_error, update = status.process()
        if do_send:
            updates.append(update)

    # making sure that Yandex Cloud Function does not timeout
    # it's okay to send edit updates a little later - during the next Function run
    return updates[:UPDATES_LIMIT]


def save_updates(ydb_pool, updates):
    db_model.update_tracker_info(ydb_pool, updates)

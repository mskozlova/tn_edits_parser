from functools import partial

from telebot import TeleBot, custom_filters

from bot import handlers as handlers
from bot import states as bot_states
from logs import logger


class Handler:
    def __init__(self, callback, **kwargs):
        self.callback = callback
        self.kwargs = kwargs


def get_start_handlers():
    return [
        Handler(callback=handlers.handle_start, commands=["start"]),
    ]


def get_track_handlers():
    return [
        Handler(callback=handlers.handle_track, commands=["track"]),
        Handler(
            callback=handlers.handle_cancel,
            commands=["cancel"],
            state=[
                bot_states.TrackState.email,
                bot_states.TrackState.password,
            ],
        ),
        Handler(
            callback=handlers.handle_email,
            state=bot_states.TrackState.email,
        ),
        Handler(
            callback=handlers.handle_password,
            state=bot_states.TrackState.password,
        ),
    ]


def get_delete_handlers():
    return [
        Handler(callback=handlers.handle_delete_account, commands=["stop"]),
        Handler(
            callback=handlers.handle_cancel,
            commands=["cancel"],
            state=[
                bot_states.DeleteState.email,
            ],
        ),
        Handler(
            callback=handlers.handle_finish_delete_account,
            state=bot_states.DeleteState.email,
        ),
    ]


def create_bot(bot_token, pool):
    state_storage = bot_states.StateYDBStorage(pool)
    bot = TeleBot(bot_token, state_storage=state_storage)

    handlers = []
    handlers.extend(get_start_handlers())
    handlers.extend(get_track_handlers())
    handlers.extend(get_delete_handlers())

    for handler in handlers:
        bot.register_message_handler(
            partial(handler.callback, pool=pool), **handler.kwargs, pass_bot=True
        )

    bot.add_custom_filter(custom_filters.StateFilter(bot))
    return bot

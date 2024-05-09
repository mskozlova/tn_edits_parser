from bot import keyboards, states
from database import model as db_model
from logs import logged_execution
from pwd_cipher import AESCipher
from tn_parser import check_password
from user_interaction import texts


@logged_execution
def handle_start(message, bot, pool):
    bot.send_message(message.chat.id, texts.START, reply_markup=keyboards.EMPTY)


@logged_execution
def handle_track(message, bot, pool):
    bot.send_message(
        message.chat.id,
        texts.EMAIL,
        reply_markup=keyboards.get_reply_keyboard(["/cancel"]),
    )
    bot.set_state(
        message.from_user.id, states.TrackState.email, message.chat.id
    )


@logged_execution
def handle_cancel(message, bot, pool):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(
        message.chat.id,
        texts.CANCEL,
        reply_markup=keyboards.EMPTY,
    )


@logged_execution
def handle_email(message, bot, pool):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["email"] = message.text.strip()
    bot.set_state(message.from_user.id, states.TrackState.password, message.chat.id)
    bot.send_message(
        message.chat.id,
        texts.PASSWORD,
        reply_markup=keyboards.get_reply_keyboard(["/cancel"]),
    )


@logged_execution
def handle_password(message, bot, pool):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        email = data["email"]
        password = AESCipher().encrypt(message.text.strip())

    is_password_ok = check_password(email, password)
    bot.delete_state(message.from_user.id, message.chat.id)
    
    if is_password_ok:
        db_model.add_tracking(pool, message.chat.id, email, password)
        bot.send_message(
            message.chat.id,
            texts.TRACKING_STARTED.format(email),
            reply_markup=keyboards.EMPTY,
        )
    else:
        bot.send_message(
            message.chat.id,
            texts.TRACKING_FAILED,
            reply_markup=keyboards.EMPTY,
        )
        
    # deleting password from the chat history
    bot.delete_message(message.chat.id, message.id)


@logged_execution
def handle_delete_account(message, bot, pool):
    emails = db_model.get_chat_trackings(pool, message.chat.id)

    bot.send_message(
        message.chat.id,
        texts.EMAIL_TO_DELETE.format("\n".join(sorted(emails))),
        reply_markup=keyboards.get_reply_keyboard(["/cancel"]),
    )
    bot.set_state(message.from_user.id, states.DeleteState.email, message.chat.id)


@logged_execution
def handle_finish_delete_account(message, bot, pool):
    email = message.text.strip()
    bot.delete_state(message.from_user.id, message.chat.id)
    db_model.delete_tracking(pool, message.chat.id, email)
    bot.send_message(
        message.chat.id,
        texts.EMAIL_DELETED,
        reply_markup=keyboards.EMPTY,
    )

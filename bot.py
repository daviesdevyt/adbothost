from telebot import TeleBot
from telebot.types import CallbackQuery, Message
from .tgkeyboards import *
from .db import session, User
from .config import bot_token, owner
from datetime import datetime

bot = TeleBot(bot_token, parse_mode="HTML")

start_message = "<b>Let’s get started</b> 🎉\n\nPlease tap the button below to subscribe!"


@bot.message_handler(commands=['help', 'start'])
def start(message: Message):
    bot.clear_step_handler(message)
    bot.reply_to(message, start_message,
                 reply_markup=start_inline_markup(message.chat.id))


@bot.message_handler(commands=["admin"], func=lambda msg: msg.chat.id == owner)
def admin(message: Message):
    bot.clear_step_handler(message)
    bot.send_message(
        message.chat.id, "<b>Welcome back Admin!!</b>\nWhat will you like to do today?", reply_markup=Admin.get_kb())


@bot.callback_query_handler(func=lambda call: call.data != None)
def account(callback: CallbackQuery):
    message = callback.message
    data = callback.data

    if data == "back":
        bot.clear_step_handler(message)
        bot.edit_message_text(start_message, chat_id=message.chat.id, message_id=message.id,
                              reply_markup=start_inline_markup(message.chat.id))
        return

    if data.startswith("admin_") and message.chat.id == owner:
        data = data.strip("admin_")
        if data == "get_all":
            all_users = session.query(User).all()
            msg = "\n".join(map(generate, all_users))
            if msg == "":
                msg = "No users found"
            bot.edit_message_text("To see details about any of them, Just click on their ids\n\n"+msg,
                                  message.chat.id, message.id, parse_mode="markdown", reply_markup=Admin.get_kb())
            bot.register_next_step_handler(message, get_subscriber_data)
        elif data == "back":
            bot.edit_message_text("<b>Welcome back Admin!!</b>\nWhat will you like to do today?",
                                  message.chat.id, message.id, reply_markup=Admin.get_kb())
        return

    user = session.query(User).get(message.chat.id)
    if not user or user.end_time < datetime.now():
        web_app = WebAppInfo(url=url+f"?user_id={message.chat.id}")
        order_inline_btn = InlineKeyboardButton("ORDER NOW", web_app=web_app)
        markup = InlineKeyboardMarkup()
        markup.add(order_inline_btn)
        bot.edit_message_text(f"Your telegram ID: `{message.chat.id}`\n\nYou have no active subscription.\nUse the button below to choose a subscription",
                              message.chat.id, message.id, reply_markup=start_inline_markup(message.chat.id), parse_mode="markdown")
        return

    if data == "account":
        bot.clear_step_handler(message)
        bot.edit_message_text(f"Hello <b>{message.chat.username}</b>.\nWhat do you want to do today?",
                              message.chat.id, message.id, reply_markup=account_markup)

    if data == "edit_message":
        bot.send_message(
            message.chat.id, f"Current: `{user.message}`\n\nSend the new message you want to set", parse_mode="markdown")
        bot.register_next_step_handler(message, set_message)


def get_subscriber_data(message: Message):
    uid = message.text[1:]
    try:
        user = session.query(User).get(int(uid))
        if not user:
            raise Exception()
    except ValueError:
        if uid == 'start':
            start(message)
            return
        admin(message)
        return
    except:
        bot.reply_to(message, f"User \"{uid}\" doesnt exist")
        bot.clear_step_handler(message)
        return
    end = user.end_time.strftime("%I:%M %p %d %b, %Y")
    bot.send_message(message.chat.id, f"User ID: {uid}\nUsername: {bot.get_chat(uid).username}\n"
                     f"\nPackage: {user.package} Groups\nExpiring: {end}"
                     f"\nMessage: `{user.message}`", parse_mode="markdown", reply_markup=Admin.get_kb())
    bot.register_next_step_handler(message, get_subscriber_data)


def generate(user: User):
    end = user.end_time.strftime("%I:%M %p %d %b")
    return f"/{user.id} - Expiring {end}"


def set_message(message: Message):
    user = session.query(User).get(message.chat.id)
    user.message = message.text
    session.commit()
    bot.reply_to(message, f"Message updated !! to {message.text}")
    bot.send_message(
        owner, f"Newest Message from @{message.chat.username}\n\n{message.text}")


@bot.message_handler(func=lambda message: True)
def echo_message(message: Message):
    start(message)

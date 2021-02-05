import os
import redis
from dotenv import load_dotenv
import moltin
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
import utils

_database = None
load_dotenv()


def start(bot, update):
    products = moltin.get_products()
    keyboard = [[InlineKeyboardButton(
        product['name'], callback_data=product['id'])] for product in products]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(bot, update):
    query = update.callback_query

    keyboard = [[InlineKeyboardButton('1 кг', callback_data=f'1kg, {query.data}'),
                 InlineKeyboardButton(
                     '5 кг', callback_data=f'5kg, {query.data}'),
                 InlineKeyboardButton('10 кг', callback_data=f'10kg, {query.data}')],
                [InlineKeyboardButton('Назад', callback_data='back')],
                [InlineKeyboardButton('Корзина', callback_data='cart')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    product_info = moltin.get_item_by_id(query.data)
    product_photo_id = product_info['relationships']['main_image']['data']['id']
    product_photo = moltin.get_photo_url_by_id(product_photo_id)

    name = product_info['name']
    description = product_info['description']
    price_per_kg = f"{product_info['meta']['display_price']['with_tax']['formatted']} per kg"
    if product_info['meta']['stock']['availability'] == 'in-stock':
        on_stock_kg = f"{product_info['meta']['stock']['level']} on stock"
    else:
        on_stock_kg = 'Товара нет в наличии'

    bot.send_photo(chat_id=query.message.chat_id,
                   photo=product_photo,
                   caption=f"{name}\n\n{price_per_kg}\n{on_stock_kg}\n\n{description}",
                   reply_markup=reply_markup)
    bot.delete_message(chat_id=query.message.chat_id,
                       message_id=query.message.message_id)
    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    query = update.callback_query
    info = query.data.split(', ')

    if info[0] == 'back':
        products = moltin.get_products()
        keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id'])] for product in products]
        keyboard.append([InlineKeyboardButton('Корзина', callback_data='cart')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.send_message(text='Please choose:',
                         reply_markup=reply_markup,
                         chat_id=query.message.chat_id)
        bot.delete_message(chat_id=query.message.chat_id,
                           message_id=query.message.message_id)
        return "HANDLE_MENU"

    elif info[0] == 'cart':
        utils.show_cart(query, bot, update)
        return "HANDLE_CART"
    elif info[0] == '1kg':
        moltin.add_product_to_cart(cart_id=query.message.chat_id,
                                   product_id=info[1],
                                   product_amount=1)
    elif info[0] == '5kg':
        moltin.add_product_to_cart(cart_id=query.message.chat_id,
                                   product_id=info[1],
                                   product_amount=5)
    elif info[0] == '10kg':
        moltin.add_product_to_cart(cart_id=query.message.chat_id,
                                   product_id=info[1],
                                   product_amount=10)


def handle_cart(bot, update):
    query = update.callback_query

    if query.data == 'menu':
        products = moltin.get_products()
        keyboard = [[InlineKeyboardButton(product['name'], callback_data=product['id'])] for product in products]
        keyboard.append([InlineKeyboardButton('Корзина', callback_data='cart')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot.edit_message_text(text='Please choose:',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=reply_markup)
        return "HANDLE_MENU"
    elif query.data == 'payment':
        bot.edit_message_text(text='Введите email для связи',
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return "WAITING_EMAIL"
    else:
        moltin.delete_item_from_cart(query.message.chat_id, query.data)
        utils.show_cart(query, bot, update)
        return "HANDLE_CART"


def handle_email(bot, update):
    first_name = update['message']['chat']['first_name']
    last_name = update['message']['chat']['last_name']
    email = update.message.text

    moltin.create_customer(first_name, last_name, email)
    bot.send_message(text=f'Вы прислали мне этот email: {email}\nС вами скоро свяжуться',
                     chat_id=update.message.chat_id)


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': handle_email
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(bot, update)
    db.set(chat_id, next_state)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv("REDIS_PASSWORD")
        database_host = os.getenv("REDIS_HOST")
        database_port = os.getenv("REDIS_PORT")
        _database = redis.Redis(
            host=database_host, port=database_port, password=database_password)
    return _database


def error_callback(bot, update, error):
    try:
        logging.error(str(update))
        update.message.reply_text(text='Простите, возникла ошибка.')
    except Exception as err:
        logging.critical(err)


if __name__ == '__main__':
    token = os.getenv("TG_BOT_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_error_handler(error_callback)

    updater.start_polling()

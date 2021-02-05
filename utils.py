import moltin
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def show_cart(query, bot, update):
    products = moltin.get_cart_items(query.message.chat_id)

    list_reply = []
    total = sum([product['meta']['display_price']['with_tax']['value']['amount'] for product in products])
    for product in products:
        name = product['name']
        description = product['description']
        numbers = product['quantity']
        price = product['meta']['display_price']['with_tax']
        price_per_kg = price['unit']['formatted']
        total_price = price['value']['formatted']
        list_reply.append(f"{name}\n{description}\n{price_per_kg} per kg\n{numbers}kg in cart for {total_price}\n\n")
    list_reply.append(f'Total price: ${total / 100:.2f}')
    reply = ''.join(list_reply)

    keyboard = [[InlineKeyboardButton(f"Удалить товар {product['name']}", callback_data=product['id'])] for product in products]
    keyboard.append([InlineKeyboardButton('В меню', callback_data='menu')])
    keyboard.append([InlineKeyboardButton('Оплата', callback_data='payment')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(text=reply,
                     reply_markup=reply_markup,
                     chat_id=query.message.chat_id)
    bot.delete_message(chat_id=query.message.chat_id,
                       message_id=query.message.message_id)
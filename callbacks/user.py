from data.globals import bd
from data.offer_reply import OfferReply
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from offers.offer_list import offer_list


def main_menu_callback(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()

    keyboard = [[InlineKeyboardButton("Список предложений", callback_data='offer_list')],
                [InlineKeyboardButton("Мои заявки", callback_data='request_list')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text="Здравствуйте, пользователь")
    query.edit_message_reply_markup(reply_markup=reply_markup)


def offer_list_callback(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()

    keyboard = []
    offers = "Список предложений:\n"
    for ind, offer in enumerate(offer_list):
        offers += f'{ind + 1}: ' + offer.description + "\n"
        keyboard.append([InlineKeyboardButton(offer.description, callback_data=f'offer_list/{ind}')])
    keyboard.append([InlineKeyboardButton("<<Назад", callback_data=f'main_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=offers)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def credit_choosen_callback(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    offer_ind = int(query.data.split("/")[-1])

    keyboard = [
        [InlineKeyboardButton("Оформить заявку", callback_data=f'offer_list/{offer_ind}/fill')],
        [InlineKeyboardButton("<<Назад", callback_data=f'offer_list')]]
    offer = "Информация о предложении:\n" + offer_list[offer_ind].constructor()().descry

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=offer)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def request_list_callback(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    chat_id = int(query.message.chat.id)

    requests = bd.get_replies(chat_id)
    keyboard = []
    description_text = ""
    for ind, request_data in enumerate(requests):
        offer_reply = OfferReply.from_bd_row(**request_data, row_ind=ind)
        if offer_reply.is_deleted():
            continue

        description_text += f'{ind + 1}: ' + offer_reply.credit_description() + "\n"
        keyboard.append([InlineKeyboardButton(offer_reply.credit_description(),
                                              callback_data=f'request_list/{ind}')])
    if len(keyboard) != 0:
        text = "Список заявок:\n" + description_text
    else:
        text = "Список ваших заявок пуст"

    keyboard.append([InlineKeyboardButton("<<Назад", callback_data=f'main_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def request_choosen_callback(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    chat_id = int(query.message.chat.id)
    request_ind = int(query.data.split("/")[-1])

    requests = bd.get_replies(chat_id)
    offer_reply = OfferReply.from_bd_row(**requests[request_ind], row_ind=request_ind)

    keyboard = [
        [InlineKeyboardButton("Удалить", callback_data=f'request_list/{request_ind}/delete')],
        [InlineKeyboardButton("<<Назад", callback_data=f'request_list')]
    ]

    text = offer_reply.get_reply()

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def request_delete_callback(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    chat_id = int(query.message.chat.id)
    request_ind = int(query.data.split("/")[1])

    requests = bd.get_replies(chat_id)
    offer_reply = OfferReply.from_bd_row(**requests[request_ind], row_ind=request_ind)
    offer_reply.delete()
    bd.write_reply(offer_reply)

    keyboard = [[InlineKeyboardButton("<<Назад", callback_data=f'request_list')]]

    text = "Удалено"

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)

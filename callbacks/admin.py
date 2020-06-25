from data.globals import bd
from data.offer_reply import OfferReply
from messaging.globals import notifier
from messaging.message import Message
import telegram
from telegram.ext import Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Ожидают рассмотрения",
                              callback_data=f'admin_check_replies')],
        [InlineKeyboardButton("Одобренные",
                              callback_data=f'admin_approved_replies')],
        [InlineKeyboardButton("Отклонённые",
                              callback_data=f'admin_rejected_replies')],
    ]
    text = "Здравствуйте, администратор"

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_check_replies(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()

    keyboard = []

    bd.filter_reply_queue()
    if len(bd.reply_to_approve_queue) != 0:
        for ind, or_address in enumerate(bd.reply_to_approve_queue):
            offer_reply = bd.get_reply(or_address)
            if offer_reply.is_deleted():
                continue
            keyboard.append([InlineKeyboardButton(offer_reply.admin_description(),
                                                  callback_data=f'admin_check_replies/{ind}')])
        text = "Доступные заявки"
    else:
        text = "Очередь пуста"

    keyboard.append([InlineKeyboardButton("Обновить список",
                                          callback_data=f'admin_check_replies')])
    keyboard.append([InlineKeyboardButton("<<Назад",
                                          callback_data=f'admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_view_reply(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    reply_ind = int(query.data.split("/")[-1])
    offer_reply = bd.get_reply(bd.reply_to_approve_queue[reply_ind])
    if offer_reply.is_deleted():
        text = "Заявка была удалена пользователем"
        keyboard = []
    else:
        keyboard = [[InlineKeyboardButton("Одобрить",
                                          callback_data=f'admin_check_replies/{reply_ind}/approve'),
                     InlineKeyboardButton("Отклонить",
                                          callback_data=f'admin_check_replies/{reply_ind}/reject')]]
        text = "Заявка: \n" + str(offer_reply)
    keyboard.append([InlineKeyboardButton("<<Назад",
                                          callback_data=f'admin_check_replies')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_approve_reply(update, context: telegram.ext.CallbackContext):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    reply_ind = int(query.data.split("/")[1])
    offer_reply: OfferReply = bd.get_reply(bd.reply_to_approve_queue.pop(reply_ind))
    if offer_reply.is_deleted():
        text = "Заявка была удалена пользователем"
    else:
        offer_reply.approve()
        bd.flush()
        bd.write_reply(offer_reply)
        notifier.send_edited_reply(offer_reply)
        text = "Одобрено"

    keyboard = [[InlineKeyboardButton("<<Назад", callback_data=f'admin_check_replies')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_reject_reply(update, context: telegram.ext.CallbackContext):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    reply_ind = int(query.data.split("/")[1])
    offer_reply: OfferReply = bd.get_reply(bd.reply_to_approve_queue.pop(reply_ind))
    if offer_reply.is_deleted():
        text = "Заявка была удалена пользователем"
    else:
        offer_reply.reject()
        bd.write_reply(offer_reply)
        bd.flush()
        notifier.send_edited_reply(offer_reply)
        text = "Отклонено"

    keyboard = [[InlineKeyboardButton("<<Назад", callback_data=f'admin_check_replies')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_approved_replies(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()

    keyboard = []

    replies = bd.get_approved_replies()
    if len(replies) != 0:
        for ind, or_address in enumerate(replies):
            offer_reply = bd.get_reply(or_address)
            if offer_reply.is_deleted():
                continue
            keyboard.append([InlineKeyboardButton(offer_reply.admin_description(),
                                                  callback_data=f'admin_approved_replies/{or_address.chat_id}/{or_address.user_reply_ind}/view')])
        text = "Одобренные заявки"
    else:
        text = "Список пуст"

    keyboard.append([InlineKeyboardButton("Обновить список",
                                          callback_data=f'admin_approved_replies')])
    keyboard.append([InlineKeyboardButton("<<Назад",
                                          callback_data=f'admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_view_approved_reply(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    chat_id, reply_ind = tuple(map(int, query.data.split("/")[1:3]))
    keyboard = []

    offer_reply = bd.get_reply(OfferReply.Address(chat_id, reply_ind))
    if offer_reply.is_deleted():
        text = "Заявка была удалена пользователем"
    else:
        text = offer_reply.get_reply(admin=True)

    keyboard.append([InlineKeyboardButton("<<Назад",
                                          callback_data=f'admin_approved_replies')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_rejected_replies(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()

    keyboard = []

    replies = bd.get_rejected_replies()
    if len(replies) != 0:
        for ind, or_address in enumerate(replies):
            offer_reply = bd.get_reply(or_address)
            if offer_reply.is_deleted():
                continue
            keyboard.append([InlineKeyboardButton(offer_reply.admin_description(),
                                                  callback_data=f'admin_rejected_replies/{or_address.chat_id}/{or_address.user_reply_ind}/view')])
        text = "Отклонённые заявки"
    else:
        text = "Список пуст"

    keyboard.append([InlineKeyboardButton("Обновить список",
                                          callback_data=f'admin_rejected_replies')])
    keyboard.append([InlineKeyboardButton("<<Назад",
                                          callback_data=f'admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)


def admin_view_rejected_reply(update, context):
    query: telegram.CallbackQuery = update.callback_query
    query.answer()
    chat_id, reply_ind = tuple(map(int, query.data.split("/")[1:3]))
    keyboard = []

    offer_reply = bd.get_reply(OfferReply.Address(chat_id, reply_ind))
    if offer_reply.is_deleted():
        text = "Заявка была удалена пользователем"
    else:
        text = offer_reply.get_reply(admin=True)

    keyboard.append([InlineKeyboardButton("<<Назад",
                                          callback_data=f'admin_rejected_replies')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=text)
    query.edit_message_reply_markup(reply_markup=reply_markup)

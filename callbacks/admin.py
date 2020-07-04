from data.offer_reply import OfferReply
import telegram
from telegram.ext import Updater
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class AdminCallback:

    def __init__(self, notifier, bd):
        self.bd = bd
        self.notifier = notifier

    def menu(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()

        keyboard = [
            [InlineKeyboardButton("Ожидают рассмотрения",
                                  callback_data=f'admin_check_replies')],
            [InlineKeyboardButton("Одобренные",
                                  callback_data=f'admin_approved_replies')],
            [InlineKeyboardButton("Отклонённые",
                                  callback_data=f'admin_rejected_replies')],
            [InlineKeyboardButton("Отменённые",
                                  callback_data=f'admin_cancelled_replies')],
        ]
        text = "Здравствуйте, администратор"

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def check_replies(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()

        keyboard = []

        self.bd.filter_reply_queue()
        if len(self.bd.reply_to_approve_queue) != 0:
            for ind, or_address in enumerate(self.bd.reply_to_approve_queue):
                offer_reply = self.bd.get_reply(or_address)
                if offer_reply.is_removed():
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

    def view_pending_reply(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        reply_ind = int(query.data.split("/")[-1])
        offer_reply: OfferReply = self.bd.get_reply(self.bd.reply_to_approve_queue[reply_ind])
        text = ""
        if offer_reply.is_cancelled():
            text = "Заявка была отменена пользователем\n"
            keyboard = []
        elif offer_reply.is_removed():
            text = "Заявка была удалена"
            keyboard = []
        else:
            keyboard = [[InlineKeyboardButton("Одобрить",
                                              callback_data=f'admin_check_replies/{reply_ind}/approve'),
                         InlineKeyboardButton("Отклонить",
                                              callback_data=f'admin_check_replies/{reply_ind}/reject')]]
        text += "Заявка: \n" + str(offer_reply)
        keyboard.append([InlineKeyboardButton("<<Назад",
                                              callback_data=f'admin_check_replies')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def approve_reply(self, update, context: telegram.ext.CallbackContext):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        reply_ind = int(query.data.split("/")[1])
        if reply_ind >= len(self.bd.reply_to_approve_queue):
            text = "Неверный индекс"
        else:
            offer_reply: OfferReply = self.bd.get_reply(self.bd.reply_to_approve_queue.pop(reply_ind))

            if offer_reply.is_cancelled():
                text = "Заявка была отменена пользователем\n"
            elif offer_reply.is_removed():
                text = "Заявка была удалена"
            else:
                offer_reply.approve()
                self.bd.write_reply(offer_reply)
                self.bd.flush()
                self.notifier.send_edited_reply(offer_reply)
                text = "Одобрено"

        keyboard = [[InlineKeyboardButton("<<Назад", callback_data=f'admin_check_replies')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def reject_reply(self, update, context: telegram.ext.CallbackContext):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        reply_ind = int(query.data.split("/")[1])

        if reply_ind >= len(self.bd.reply_to_approve_queue):
            text = "Неверный индекс"
        else:
            offer_reply: OfferReply = self.bd.get_reply(self.bd.reply_to_approve_queue.pop(reply_ind))
            if offer_reply.is_cancelled():
                text = "Заявка была отменена пользователем\n"
            elif offer_reply.is_removed():
                text = "Заявка была удалена\n"
            else:
                offer_reply.reject()
                self.bd.write_reply(offer_reply)
                self.bd.flush()
                self.notifier.send_edited_reply(offer_reply)
                text = "Отклонено"

        keyboard = [[InlineKeyboardButton("<<Назад", callback_data=f'admin_check_replies')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def approved_replies(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()

        keyboard = []

        replies = self.bd.get_approved_replies()
        if len(replies) != 0:
            for ind, or_address in enumerate(replies):
                offer_reply = self.bd.get_reply(or_address)
                if offer_reply.is_removed():
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

    def view_reply(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        return_way = query.data.split("/")[0]
        chat_id, reply_ind = tuple(map(int, query.data.split("/")[1:3]))
        keyboard = []

        offer_reply = self.bd.get_reply(OfferReply.Address(chat_id, reply_ind))

        if offer_reply is None:
            text = "Неверный адрес"
        else:
            text = ""
            if offer_reply.is_removed():
                text = "Заявка была удалена\n"
            else:
                keyboard.append([InlineKeyboardButton("Удалить",
                                                      callback_data=f'{return_way}/{chat_id}/{reply_ind}/remove')])

            if offer_reply.is_cancelled():
                text = "Заявка была отменена пользователем\n"
            text += offer_reply.get_reply(admin=True)

        keyboard.append([InlineKeyboardButton("<<Назад",
                                              callback_data=f'{return_way}')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def view_approved_reply(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        chat_id, reply_ind = tuple(map(int, query.data.split("/")[1:3]))
        keyboard = []

        offer_reply = self.bd.get_reply(OfferReply.Address(chat_id, reply_ind))

        if offer_reply is None:
            text = "Неверный адрес"
        else:
            text = ""
            if offer_reply.is_cancelled():
                text = "Заявка была отменена пользователем\n"
            elif offer_reply.is_removed():
                text = "Заявка была удалена\n"
            else:
                keyboard.append([InlineKeyboardButton("Удалить",
                                                      callback_data=f'admin_approved_replies/{chat_id}/{reply_ind}/remove')])
            text += offer_reply.get_reply(admin=True)

        keyboard.append([InlineKeyboardButton("<<Назад",
                                              callback_data=f'admin_approved_replies')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def rejected_replies(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()

        keyboard = []

        replies = self.bd.get_rejected_replies()
        if len(replies) != 0:
            for ind, or_address in enumerate(replies):
                offer_reply = self.bd.get_reply(or_address)
                if offer_reply.is_removed():
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

    def view_rejected_reply(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        chat_id, reply_ind = tuple(map(int, query.data.split("/")[1:3]))
        keyboard = []

        offer_reply = self.bd.get_reply(OfferReply.Address(chat_id, reply_ind))

        if offer_reply is None:
            text = "Неверный адрес"
        else:
            text = ""
            if offer_reply.is_cancelled():
                text = "Заявка была отменена пользователем\n"
            elif offer_reply.is_removed():
                text = "Заявка была удалена\n"
            else:
                keyboard.append([InlineKeyboardButton("Удалить",
                                                  callback_data=f'admin_rejected_replies/{chat_id}/{reply_ind}/remove')])
            text += offer_reply.get_reply(admin=True)

        keyboard.append([InlineKeyboardButton("<<Назад",
                                              callback_data=f'admin_rejected_replies')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def cancelled_replies(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()

        keyboard = []

        replies = self.bd.get_cancelled_replies()
        if len(replies) != 0:
            for ind, or_address in enumerate(replies):
                offer_reply = self.bd.get_reply(or_address)
                if offer_reply.is_removed():
                    continue
                keyboard.append([InlineKeyboardButton(offer_reply.admin_description(),
                                                      callback_data=f'admin_cancelled_replies/{or_address.chat_id}/{or_address.user_reply_ind}/view')])
            text = "Отменённые заявки"
        else:
            text = "Список пуст"

        keyboard.append([InlineKeyboardButton("Обновить список",
                                              callback_data=f'admin_cancelled_replies')])
        keyboard.append([InlineKeyboardButton("<<Назад",
                                              callback_data=f'admin_menu')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def view_cancelled_reply(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        chat_id, reply_ind = tuple(map(int, query.data.split("/")[1:3]))
        keyboard = []

        offer_reply = self.bd.get_reply(OfferReply.Address(chat_id, reply_ind))

        if offer_reply is None:
            text = "Неверный адрес"
        else:
            text = ""
            if offer_reply.is_cancelled():
                keyboard.append([InlineKeyboardButton("Удалить",
                                                      callback_data=f'admin_cancelled_replies/{chat_id}/{reply_ind}/remove')])
            elif offer_reply.is_removed():
                text = "Заявка была удалена\n"
            text += offer_reply.get_reply(admin=True)

        keyboard.append([InlineKeyboardButton("<<Назад",
                                              callback_data=f'admin_cancelled_replies')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def remove_reply(self, update, context):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        return_way = query.data.split("/")[0]
        chat_id, reply_ind = tuple(map(int, query.data.split("/")[1:3]))
        keyboard = []
        offer_reply: OfferReply = self.bd.get_reply(OfferReply.Address(chat_id, reply_ind))

        if offer_reply is None:
            text = "Неверный адрес"
        else:
            offer_reply.remove()
            self.bd.write_reply(offer_reply)
            self.bd.flush()
            text = "Заявка была удалена\n"
            text += offer_reply.get_reply(admin=True)

        keyboard.append([InlineKeyboardButton("<<Назад",
                                              callback_data=return_way)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text)
        query.edit_message_reply_markup(reply_markup=reply_markup)

import logging

import telegram
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, Filters

from data.json_database import JsonDatabase
from messaging.notifyer import Notifier
from messaging.message import MessageType
from generators.generators import Generators
from callbacks.admin import AdminCallback
from callbacks.user import UserCallbacks

from offers.offer_list import offer_list
from static_info import MY_ID

logger = logging.getLogger(__name__)

class MyBot:

    def __init__(self, token):
        self.__notifier = Notifier()
        self.__bd = JsonDatabase()

        self.__user_callbacks = UserCallbacks(offer_list=offer_list, bd=self.__bd)
        self.__admin_callbacks = AdminCallback(notifier=self.__notifier, bd=self.__bd)
        self.__generators = Generators(offer_list=offer_list, notifier=self.__notifier, bd=self.__bd)

        self.__updater = Updater(token=token, use_context=True)

        self.__install_callbacks()

        self.__admin_generator = self.__generators.admin_generator
        self.__generator = self.__generators.user_default_generator
        self.__handlers = dict()

    def __install_callbacks(self):

        self.__updater.dispatcher.add_handler(CommandHandler("start", self.__handle_start))
        self.__updater.dispatcher.add_handler(CommandHandler("menu", self.__handle_menu))
        self.__updater.dispatcher.add_handler(MessageHandler(Filters.text | Filters.contact, self.__handle_message))

        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__user_callbacks.main_menu_callback, pattern="main_menu$"))

        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__user_callbacks.offer_list_callback, pattern="offer_list$"))
        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__user_callbacks.credit_choosen_callback, pattern="offer_list/\d+$"))
        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__credit_filling_callback, pattern="offer_list/\d+/fill$"))

        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__user_callbacks.request_list_callback, pattern="request_list$"))
        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__user_callbacks.request_choosen_callback, pattern="request_list/\d+$"))
        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__user_callbacks.request_cancel_callback, pattern="request_list/\d+/cancel$"))

        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__admin_callbacks.menu, pattern="admin_menu$"))

        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__admin_callbacks.check_replies, pattern="admin_check_replies$"))
        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__admin_callbacks.view_pending_reply, pattern="admin_check_replies/\d+$"))
        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__admin_callbacks.approve_reply, pattern="admin_check_replies/\d+/approve$"))
        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__admin_callbacks.reject_reply, pattern="admin_check_replies/\d+/reject$"))

        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__admin_callbacks.approved_replies, pattern="admin_approved_replies$"))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__admin_callbacks.view_reply,
                                                                   pattern="admin_approved_replies/\d+/\d+/view$"))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__admin_callbacks.remove_reply,
                                                                   pattern="admin_approved_replies/\d+/\d+/remove$"))

        self.__updater.dispatcher.add_handler(
            CallbackQueryHandler(self.__admin_callbacks.rejected_replies, pattern="admin_rejected_replies$"))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__admin_callbacks.view_reply,
                                                                   pattern="admin_rejected_replies/\d+/\d+/view$"))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__admin_callbacks.remove_reply,
                                                                           pattern="admin_rejected_replies/\d+/\d+/remove$"))

        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__admin_callbacks.cancelled_replies,
                                                                   pattern="admin_cancelled_replies$"))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__admin_callbacks.view_reply,
                                                                   pattern="admin_cancelled_replies/\d+/\d+/view$"))
        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__admin_callbacks.remove_reply,
                                                                   pattern="admin_cancelled_replies/\d+/\d+/remove$"))

        self.__updater.dispatcher.add_handler(CallbackQueryHandler(self.__handle_callback))
        self.__updater.dispatcher.add_error_handler(self.__error_callback)

    def start(self):
        # Начинаем поиск обновлений
        self.__updater.start_polling(clean=True)
        logger.info('Init successful. Polling...')
        print('Init successful. Polling...')
        # Останавливаем бота, если были нажаты Ctrl + C
        self.__updater.idle()
        self.__bd.flush()
        logger.info('Bot is off')
        print('Bot is off')

    def __send_gen_message(self, chat_id:int, update: telegram.Update, context: telegram.ext.CallbackContext):
        bot = context.bot

        if chat_id not in self.__handlers:
            if chat_id == MY_ID:
                self.__handlers[chat_id] = self.__admin_generator()
            else:
                self.__handlers[chat_id] = self.__generator()
            next(self.__handlers[chat_id])

        try:
            answer = self.__handlers[chat_id].send(update)
        except StopIteration:
            del self.__handlers[chat_id]
            return self.__handle_message(update, context)

        # отправляем полученный ответ пользователю
        answer.send(bot, chat_id)

        # если ответ на сообщение не требуется, отправим сразу следующее
        if not answer.require_response():
            self.__send_gen_message(chat_id, update, context)


    def __handle_message(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        chat_id = int(update.message.chat.id)
        self.__send_gen_message(chat_id, update, context)


    def __handle_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        print("Unexpected callback", update.callback_query.data)
        logger.info('Unexpected callback "%s"', update.callback_query.data)
        query: telegram.CallbackQuery = update.callback_query
        query.answer()


    def __credit_filling_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        credit_ind = int(query.data.split("/")[1])
        chat_id = int(query.message.chat.id)
        self.__handlers[chat_id] = self.__generators.credit_filling(credit_ind)
        next(self.__handlers[chat_id])
        self.__send_gen_message(chat_id, update, context)

    def __handle_start(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        self.__notifier.init(context.bot)
        chat_id = int(update.message.chat_id)
        self.__handlers.pop(chat_id, None)
        self.__send_gen_message(chat_id, update, context)

    def __handle_menu(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        chat_id = int(update.message.chat_id)
        self.__handlers[chat_id] = self.__generator()
        next(self.__handlers[chat_id])
        self.__send_gen_message(chat_id, update, context)

    def __error_callback(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

import logging

from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, Filters

from callbacks.admin import *
from generators.generators import *
from callbacks.user import *
from static_info import MY_ID


logger = logging.getLogger(__name__)
class MyBot:

    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)

        self.updater.dispatcher.add_handler(CommandHandler("start", self.handle_start))
        self.updater.dispatcher.add_handler(CommandHandler("menu", self.handle_menu))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text | Filters.contact, self.handle_message))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(main_menu_callback, pattern="main_menu$"))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(offer_list_callback, pattern="offer_list$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(credit_choosen_callback, pattern="offer_list/\d+$"))
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(self.credit_filling_callback, pattern="offer_list/\d+/fill$"))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(request_list_callback, pattern="request_list$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(request_choosen_callback, pattern="request_list/\d+$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(request_delete_callback, pattern="request_list/\d+/delete$"))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_menu, pattern="admin_menu$"))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_check_replies, pattern="admin_check_replies$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_view_reply, pattern="admin_check_replies/\d+$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_approve_reply, pattern="admin_check_replies/\d+/approve$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_reject_reply, pattern="admin_check_replies/\d+/reject$"))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_approved_replies, pattern="admin_approved_replies$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_view_approved_reply, pattern="admin_approved_replies/\d+/\d+/view$"))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_rejected_replies, pattern="admin_rejected_replies$"))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(admin_view_rejected_reply, pattern="admin_rejected_replies/\d+/\d+/view$"))

        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.handle_callback))
        self.updater.dispatcher.add_error_handler(self.error_callback)


        self.admin_generator = admin_generator
        self.generator = user_default_generator
        self.handlers = dict()

    def start(self):
        # Начинаем поиск обновлений
        self.updater.start_polling(clean=True)
        logger.info('Init successful. Polling...')
        print('Init successful. Polling...')
        # Останавливаем бота, если были нажаты Ctrl + C
        self.updater.idle()
        bd.flush()
        logger.info('Bot is off')
        print('Bot is off')

    def send_gen_message(self, chat_id:int, update: telegram.Update, context: telegram.ext.CallbackContext):
        bot = context.bot

        if chat_id not in self.handlers:
            if chat_id == MY_ID:
                self.handlers[chat_id] = self.admin_generator()
            else:
                self.handlers[chat_id] = self.generator()
            next(self.handlers[chat_id])

        try:
            answer = self.handlers[chat_id].send(update)
        except StopIteration:
            del self.handlers[chat_id]
            return self.handle_message(update, context)

        # отправляем полученный ответ пользователю
        answer.send(bot, chat_id)

        # если ответ на сообщение не требуется, отправим сразу следующее
        if answer.message_type == MessageType.not_require_response:
            self.send_gen_message(chat_id, update, context)


    def handle_message(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        chat_id = int(update.message.chat.id)
        self.send_gen_message(chat_id, update, context)


    def handle_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        print("Unexpected callback", update.callback_query.data)
        logger.info('Unexpected callback "%s"', update.callback_query.data)
        query: telegram.CallbackQuery = update.callback_query
        query.answer()


    def credit_filling_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        query: telegram.CallbackQuery = update.callback_query
        query.answer()
        credit_ind = int(query.data.split("/")[1])
        chat_id = int(query.message.chat.id)
        self.handlers[chat_id] = credit_filling(credit_ind)
        next(self.handlers[chat_id])
        self.send_gen_message(chat_id, update, context)

    def handle_start(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        notifier.init(context.bot)
        chat_id = int(update.message.chat_id)
        self.handlers.pop(chat_id, None)
        self.send_gen_message(chat_id, update, context)

    def handle_menu(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        chat_id = int(update.message.chat_id)
        self.handlers[chat_id] = self.generator()
        next(self.handlers[chat_id])
        self.send_gen_message(chat_id, update, context)

    def error_callback(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

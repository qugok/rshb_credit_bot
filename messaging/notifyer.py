from data.offer_reply import OfferReply
from static_info import MY_ID
from messaging.message import Message


class Notifier:
    def __init__(self, bot=None, chat_id=MY_ID):
        self.__bot = bot
        self.__admin_chat_id = chat_id

    def init(self, bot, chat_id=MY_ID):
        self.__bot = bot
        self.__admin_chat_id = chat_id

    def notify(self):
        if self.__bot is None or self.__admin_chat_id is None:
            return False
        message = Message("Новая заявка").make_inline_keyboard([[("Посмотреть список заявок", "admin_check_replies")]])
        message.send(self.__bot, self.__admin_chat_id)
        return True

    def send_edited_reply(self, reply: OfferReply):
        message = Message(reply.get_reply(True), clear=False)
        message.send(self.__bot, reply.__chat_id)
import telegram
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from enum import Enum, auto

from messaging.utils import split


class MessageType(Enum):
    require_response = auto()
    not_require_response = auto()


class Message:

    def __init__(self, *texts, message_type=MessageType.require_response, clear=True, **options):
        if "reply_markup" not in options and clear:
            options["reply_markup"] = ReplyKeyboardRemove()

        self.__message_type = message_type
        self.__texts = texts
        self.__options = options

    def require_response(self):
        return self.__message_type == MessageType.require_response

    def send(self, bot: telegram.Bot, chat_id):
        self.__prepare()
        for text in self.__texts:
            if len(text.strip()) != 0:
                bot.sendMessage(chat_id=chat_id, text=text, **self.__options)

    def add(self, *texts: str):
        return type(self)(*texts, *self.__texts, **self.__options)

    def __prepare(self):
        texts = []
        for i in self.__texts:
            texts.extend(split(i))
        self.__texts = texts

    def __str__(self):
        return str(self.__dict__)

    def set_reply_markup(self, reply_markup):
        self.__options['reply_markup'] = reply_markup
        return self

    def make_keyboard(self, list):
        new = []
        for i in list:
            line = []
            for j in i:
                line.append(KeyboardButton(text=j))
            new.append(line)

        return self.set_reply_markup(ReplyKeyboardMarkup(new))

    def make_inline_keyboard(self, list):
        new = []
        for i in list:
            line = []
            for j in i:
                line.append(
                    InlineKeyboardButton(text=j[0], callback_data=j[1]))
            new.append(line)

        return self.set_reply_markup(InlineKeyboardMarkup(new))

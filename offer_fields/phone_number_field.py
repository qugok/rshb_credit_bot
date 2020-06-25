import telegram

from offer_fields.basic import BasicCreditField
from telegram import ReplyKeyboardMarkup, KeyboardButton
from messaging.message import Message, MessageType
import re


class PhoneNumberField(BasicCreditField):
    def __init__(self, name=None, descry=None, request=None, default_value=None):
        """
        поддерживаются только российские номера

        :param name:
        :param descry:
        :param request: то, что будет показано пользователю в качестве просьбы ввода номера телефона
        :param default_value:
        """
        if name is None:
            name = "number"
        if request is None:
            request = "Введите номер телефона"
        if descry is None:
            descry = "Номер телефона"

        super().__init__(name, descry)
        self.request = request
        self.value = default_value

    def __bool__(self):
        """
        проверяется рекурсивно
        :return: является ли поле заполнеенным
        """
        return (self.value is not None)

    def __iter__(self) -> Message:
        """
        генератор для общения с клиентом и заполнения данного поля
        работает рекурсивно
        :return: Message
        """

        def get_number(unfomatted_number: str):
            """
            #TODO проверка не только форматаб но и существования такого номера, например с помощью каких-нибудь онлайн сервисов

            поддерживаются только российские номера
            возможные форматы приёма:
            +7(XXX) - XXXX-XX-X
            8(XXX) - XXXX-XX-X
            8(XXX)-XXX-XX-XX
            и т.п

            :param unfomatted_number: неотформатированный номер
            :return: номер в формате : +7(XXX)XXX XX XX
                     None, если не удалось распознать
            """
            remove_chars = {ord(i): None for i in "()- "}
            phone_pattern = re.compile(r'(\+7)(\d{3})(\d{3})(\d{2})(\d{2})')
            pre_formatted_number = unfomatted_number.translate(remove_chars)
            if pre_formatted_number.startswith("7") and pre_formatted_number.isdecimal() and len(
                    pre_formatted_number) == 11:
                number = "+" + pre_formatted_number
            elif pre_formatted_number.startswith("+7") and pre_formatted_number[1:].isdecimal() and len(
                    pre_formatted_number) == 12:
                number = pre_formatted_number
            elif pre_formatted_number.startswith("8") and pre_formatted_number.isdecimal() and len(
                    pre_formatted_number) == 11:
                number = "+7" + pre_formatted_number[1:]
            else:
                return None

            try:
                parts = phone_pattern.match(number).groups()
                return f'{parts[0]}({parts[1]}){parts[2]}-{parts[3]}-{parts[4]}'
            except:
                return None

        if self.value is not None:
            confirmation = "Всё верно."
            keyboard = [[KeyboardButton(confirmation)], [KeyboardButton("Отправить мой номер", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard)

            update = yield Message(
                f'{self.descry}: {self.value}\n' + "Если неверно, то " + self.request.lower()
            ).set_reply_markup(reply_markup)

            answer: telegram.Message = update.message
            if answer.text is not None and answer.text == confirmation:
                return

        else:
            keyboard = [[KeyboardButton("Отправить мой номер", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            update = yield Message(self.request).set_reply_markup(reply_markup)
            answer: telegram.Message = update.message

        self.value = get_number(answer.text if answer.contact is None else answer.contact.phone_number)

        while not bool(self):
            update = yield Message(
                "Похоже я не могу распознать формат\nВведите телефон в таокм формате: +7(XXX)XXX-XX-XX\nИли отправьте свой контакт").set_reply_markup(
                reply_markup)
            answer = update.message
            self.value = get_number(answer.text if answer.contact is None else answer.contact.phone_number)

        yield Message(f'Номер введён: {self.value}', message_type=MessageType.not_require_response)

    def __repr__(self) -> str:
        """
        строковое предстваление
        для печати в логи
        применяется рекурсивно
        :return: str
        """
        return f'PhoneNumberField<{self.value}>'

    def __str__(self) -> str:
        """
        строковое представление поля
        для показа пользователю
        применяется рекурсивно
        :return: str
        """
        return (
            f'{self.descry}' + (f': {self.value}' if self.value is not None else "") if self.descry is not None else "")

    def get_info(self) -> dict:
        """
        информация, записанная в примитивных полях внутри
        применяется рекурсивно
        :return: dict (str, )
        """
        return {self.name: self.value}

    def fill_fields(self, **info):
        if self.name in info:
            self.value = info[self.name]

    def clear(self):
        self.value = None

    def admin_description(self):
        return "ph:" + str(self.value)

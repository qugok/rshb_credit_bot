import telegram

from offer_fields.basic import BasicCreditField
from messaging.message import Message, MessageType
import re


class EmailField(BasicCreditField):
    def correct_checker(self, email: str):
        """
        пропускает далеко не все адреса
        :param email:
        :return:
        """
        email_pattern = re.compile(r'([\w.]+)@(\w+).(\w+)')
        if email_pattern.match(email) is not None:
            return True
        return False

    def __init__(self, name=None, descry=None, request=None, default_value=None):
        """
        :param name:
        :param descry:
        :param request: то, что будет показано пользователю в качестве просьбы ввода
        :param default_value:
        """
        if name is None:
            name = "email"
        if request is None:
            request = "Введите адрес электронной почты"
        if descry is None:
            descry = "Почта"

        super().__init__(name, descry)
        self.request = request
        self.value = default_value

    def __bool__(self):
        """
        проверяется рекурсивно
        :return: является ли поле заполнеенным
        """
        return (self.value is not None) and self.correct_checker(self.value)

    def __iter__(self) -> Message:
        """
        генератор для общения с клиентом и заполнения данного поля
        работает рекурсивно
        :return: Message
        """

        update = yield Message(self.request)
        answer: telegram.Message = update.message
        self.value = answer.text

        while not bool(self):
            update = yield Message("Пожалуйста введите корректную или другую почту, не все форматы почт принимаются")
            answer = update.message
            self.value = answer.text

        yield Message(f'Почта введена: {self.value}', message_type=MessageType.not_require_response)

    def __repr__(self) -> str:
        """
        строковое предстваление
        для печати в логи
        применяется рекурсивно
        :return: str
        """
        return f'EmailField<{self.value}>'

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
        return "mail:" + str(self.value)

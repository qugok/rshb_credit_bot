from offer_fields.basic import BasicCreditField
from messaging.message import Message, MessageType

class IntCreditField(BasicCreditField):

    #TODO проверщик корректности может вернуть не только верно/нет, но и комментарий
    def __init__(self, name=None, descry=None, correct_checker=None, request=None, default_value=None):
        """

        :param name:
        :param descry:
        :param correct_checker: проверщик корректности, вовращает пару (bool, str) - результат и комментарий если не ок
        :param request:
        :param default_value:
        """
        super().__init__(name, descry)
        if request is None:
            request = "Выберите число"

        self.request = request
        self.correct_checker = correct_checker
        self.value = default_value
        self.comment = "Выглядит не как число. Введите число"

    def __bool__(self):
        """
        проверяется рекурсивно
        :return: является ли поле заполнеенным корректно
        """
        if self.value is not None and self.correct_checker is not None:
            self.comment = self.correct_checker(self.value)[1]
        return (self.value is not None) and (self.correct_checker(self.value)[0] if self.correct_checker is not None else True)

    def __iter__(self) -> Message:
        """
        генератор для общения с клиентом и заполнения данного поля
        работает рекурсивно
        :return: Message
        """
        update = yield Message(self.request)
        answer = update.message
        self.value = answer.text

        while not bool(self):
            update = yield Message(self.comment)
            answer = update.message
            self.value = answer.text

        yield Message(f'{self.descry}: {self.value}', message_type=MessageType.not_require_response)

    def __repr__(self) -> str:
        """
        строковое предстваление
        для печати в логи
        применяется рекурсивно
        :return: str
        """
        return f'IntField<{self.name}: {self.value}>'

    def __str__(self) -> str:
        """
        строковое представление поля
        для показа пользователю
        применяется рекурсивно
        :return: str
        """
        return (f'{self.descry}' + (f': {self.value}'if self.value is not None else "") if self.descry is not None else "")

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
        return self.name + ":" + self.value




class StringCreditField(BasicCreditField):
    def __init__(self, name=None, descry=None, correct_checker=None, default_value=None):
        super().__init__(name, descry)
        self.correct_checker = correct_checker
        self.value = default_value

    def __bool__(self):
        """
        проверяется рекурсивно
        :return: является ли поле заполнеенным
        """
        return (self.value is not None) and (self.correct_checker(self.value) if self.correct_checker is not None else True)

    def __iter__(self) -> Message:
        """
        генератор для общения с клиентом и заполнения данного поля
        работает рекурсивно
        :return: Message
        """
        #TODO дописать общение
        pass

    def __repr__(self) -> str:
        """
        строковое предстваление
        для печати в логи
        применяется рекурсивно
        :return: str
        """
        return f'StringField<{self.name}: {self.value}>'

    def __str__(self) -> str:
        """
        строковое представление поля
        для показа пользователю
        применяется рекурсивно
        :return: str
        """
        return (f'{self.descry}' + (f': {self.value}'if self.value is not None else "") if self.descry is not None else "")

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
        return self.name + ":" + self.value

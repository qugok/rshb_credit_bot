from offer_fields.basic import BasicCreditField
from messaging.message import Message, MessageType


class CreditAmountField(BasicCreditField):

    def correct_checker(self, x: str):
        if not x.isdecimal():
            return (False, "Введите число")
        elif int(x) == 0:
            return (False, "Введите положительное число")
        elif int(x) < 0:
            return (False, "Вы хотите сделать вклад?")
        elif int(x) > self.max_value:
            return (False, "Мы не выдаём такие большие суммы")
        elif 0 < int(x) < self.max_value:
            return (True, "OK")
        return (False, "Что-то пошло не так, обратитесь к человеку")

    def __init__(self, default_variants:list=None, max_value=None):
        """
        поддерживаются только российские номера

        :param name:
        :param descry:
        :param request: то, что будет показано пользователю в качестве просьбы ввода номера телефона
        :param default_value:
        """
        if max_value is None:
            max_value = 100000000000

        self.default_variants = [[str(item) for item in line] for line in default_variants]
        self.max_value = max_value
        super().__init__("amount", "Сумма кредита")
        self.request = "Введите сумму кредита в рублях"
        self.comment = "Повторите попытку"
        self.value = None

    def __bool__(self):
        """
        проверяется рекурсивно
        :return: является ли поле заполнеенным
        """
        if self.value is not None and self.correct_checker is not None:
            self.comment = self.correct_checker(self.value)[1]
        return (self.value is not None) and \
               (self.correct_checker(self.value)[0] if self.correct_checker is not None else True)

    def __iter__(self) -> Message:
        """
        генератор для общения с клиентом и заполнения данного поля
        работает рекурсивно
        :return: Message
        """

        message = Message(self.request)
        if self.default_variants is not None:
            message.make_keyboard(self.default_variants)
        update = yield message
        answer = update.message
        self.value = answer.text
        while not bool(self):
            message = Message(self.comment)
            if self.default_variants is not None:
                message.make_keyboard(self.default_variants)
            update = yield message
            answer = update.message
            self.value = answer.text

        yield Message(f'Сумма кредита: {self.value} рублей', message_type=MessageType.not_require_response)

    def __repr__(self) -> str:
        """
        строковое предстваление
        для печати в логи
        применяется рекурсивно
        :return: str
        """
        return f'CreditAmountField<{self.name}: {self.value}>'

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
        return "sum:" + self.value

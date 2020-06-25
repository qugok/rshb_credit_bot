import telegram

from offer_fields.basic import BasicCreditField
from messaging.message import Message, MessageType


class NameField(BasicCreditField):
    def __init__(self, name=None, descry=None, request=None, default_value=None, vk_field=None):
        """
        поддерживаются только российские номера

        :param name:
        :param descry:
        :param request: то, что будет показано пользователю в качестве просьбы ввода номера телефона
        :param default_value:
        """
        if name is None:
            name = "name"
        if request is None:
            request = "Введите своё имя"
        if descry is None:
            descry = "Имя"

        super().__init__(name, descry)
        self.request = request
        self.value = default_value
        self.vk_field = vk_field

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
        if self.value is not None:
            confirmation = "Всё верно."
            update = yield Message(f'{self.descry}: {self.value}\n' + "Если неверно, то " + self.request.lower()).make_keyboard([[confirmation]])
            answer:telegram.Message = update.message
            if answer.text == confirmation:
                return

        else:
            update = yield Message(self.request)
            answer:telegram.Message = update.message

        self.value = answer.text

        while not bool(self):
            update = yield Message("Что-то пошло не такю.\nПопробуйте снова.")
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
        return f'NameField<{self.value}>'

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
        return "nm:" + self.value

    def get_fields_for_vk(self):
        if self.vk_field is None:
            return []
        return [self.vk_field]

    def fill_from_vk_response(self, response):
        if self.vk_field in response:
            self.value = response[self.vk_field]
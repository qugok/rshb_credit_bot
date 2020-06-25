from messaging.message import Message

#TODO возможность формирования структуры кредита на лету из конфиг файлов

class BasicCreditField:

    #TODO для обращения и заготовки специальный текст
    def __init__(self, name: str = None, descry: str = None):
        """

        :param name: str    имя поля - видно только в __repr__
        :param descry: str   описание поля (для пользователя) - видно в __str__
        """
        if name is None:
            name = "Noname"

        self.name = name
        self.descry = descry

    def __bool__(self):
        """
        проверяется рекурсивно
        :return: является ли поле заполнеенным
        """
        return True

    def __iter__(self) -> Message:
        """
        генератор для общения с клиентом и заполнения данного поля
        работает рекурсивно
        :return: Message
        """
        pass

    def __repr__(self) -> str:
        """
        строковое предстваление
        для печати в логи
        применяется рекурсивно
        :return: str
        """
        return f'EmptyField: {self.name}'

    def __str__(self) -> str:
        """
        строковое представление поля
        для показа пользователю
        применяется рекурсивно
        :return: str
        """
        return (f'{self.descry}' if self.descry is not None else "")

    def get_info(self) -> dict:
        """
        информация, записанная в примитивных полях внутри
        применяется рекурсивно
        :return: dict (str, )
        """
        return dict()

    def fill_fields(self, **info):
        pass

    def clear(self):
        """
        полностью очищает все поля
        рекурсивно
        :return:
        """
        pass

    def admin_description(self):
        """
        строковое представление поля
        для показа администратору
        :return:
        """
        return "empty"

    def get_fields_for_vk(self):
        return []

    def fill_from_vk_response(self, response):
        pass


class CreditField(BasicCreditField):
    def __init__(self, name: str = None, descry: str = None, fields: dict = None, traversal_order=None,
                 default_values: dict = None):
        """
        :param name: str    имя поля - видно только в __repr__
        :param descry: str   описание поля (для пользователя) - видно в __str__
        :param fields: {(str, constructor T extends CreditField)}  набор полей, которые будут заполняться пользователем
                    формат - (имя: функция без агрументов, возвращающая объект класса с которым предстоит работать)
        :param traversal_order: порядок обхода (порядок для печати и для запроса у пользователя заполнения полей)
        """
        super().__init__(name, descry)

        if fields is None:
            fields = {}
        if traversal_order is None:
            traversal_order = list(fields)

        self.fields = {name: constructor() for name, constructor in fields.items()}
        self.traversal_order = traversal_order
        # self.__dict__.update(**self.fields)

        if default_values is not None:
            self.fill_fields(**default_values)

    def __bool__(self):
        """
        проверяется рекурсивно
        :return: является ли поле заполнеенным
        """
        for key, item in self.fields.items():
            if not bool(item):
                return False
        return True

    def __iter__(self):
        """
        генератор для общения с клиентом и заполнения данного поля
        работает рекурсивно
        :return: Message
        """
        for item in self.traversal_order:
            if item in self.fields:
                yield from self.fields[item]
                continue

    def __repr__(self):
        """
        строковое предстваление
        для печати в логи
        применяется рекурсивно
        :return: str
        """
        return f'CreditField: {self.name}' + "{" + ", ".join(
            [item + ": " + repr(self.fields[item]) for item in self.traversal_order if item in self.fields]) + "}"

    def __str__(self):
        """
        строковое представление поля
        для показа пользователю
        применяется рекурсивно
        :return: str
        """
        return (f'{self.descry}\n' if self.descry is not None else "") + "\n".join(
            [str(self.fields[item]) for item in self.traversal_order if item in self.fields]) + "\n"

    def get_info(self):
        """
        информация, записанная в примитивных полях внутри
        применяется рекурсивно
        :return: dict (str, )
        """
        final_dict = dict()
        for key, item in self.fields.items():
            final_dict[key] = (item.get_info())
        return final_dict

    def fill_fields(self, *args, **info):
        for field_name in self.fields:
            if field_name not in info:
                continue
            self.fields[field_name].fill_fields(**info[field_name])

    def clear(self):
        for field_name in self.fields:
            self.fields[field_name].clear()

    def admin_description(self):
        """
        строковое представление поля
        для показа администратору
        :return:
        """
        return " ".join([field.admin_description() for field in self.fields.values()])

    def fill_from_vk_response(self, response):
        for field_name in self.fields:
            self.fields[field_name].fill_from_vk_response(response)

    def get_fields_for_vk(self):
        fields = []
        for field_name in self.fields:
            fields.extend(self.fields[field_name].get_fields_for_vk())
        return fields
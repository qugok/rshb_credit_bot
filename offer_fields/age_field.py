from offer_fields.primitive_fields import IntCreditField


class AgeField(IntCreditField):

    @staticmethod
    def age_checker(age: str):
        if not age.isdecimal() and not (age[0] == '-' and age[1:].isdecimal()):
            return (False, "Введите число")
        elif int(age) <= 0:
            return (False, "Вы еще не родились? Введите корректный возраст")
        elif int(age) < 18:
            return (False, "Вы еще слишком молоды. Позовите совершеннолетнего")
        elif 0 < int(age) < 120:
            return (True, "OK")
        return (False, "Введите корректный возраст")

    def __init__(self, name=None, descry=None, request=None):
        """
        :param name:
        :param descry:
        :param request: то, что будет показано пользователю в качестве просьбы ввода
        :param default_value:
        """
        if name is None:
            name = "age"
        if request is None:
            request = "Введите ваш возраст"
        if descry is None:
            descry = "Возраст"

        super().__init__(name=name,
                         descry=descry,
                         correct_checker=AgeField.age_checker,
                         request=request)

    def __repr__(self) -> str:
        """
        строковое предстваление
        для печати в логи
        :return: str
        """
        return f'AgeField<{self.value}>'

    def admin_description(self):
        """
        строковое представление поля
        для показа администратору
        :return:
        """
        return "age:" + str(self.value)

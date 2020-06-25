from offer_fields.basic import CreditField
from offer_fields.email_field import EmailField
from offer_fields.name_field import NameField
from offer_fields.phone_number_field import PhoneNumberField
from offers.offer import Offer


class BankCard(Offer):
    description = "Просто карта банка"
    need_vk = True
    vk_fields = "Имя"

    @staticmethod
    def constructor():
        class Card(CreditField):
            def __init__(self):
                super().__init__(name="card",
                                 descry="Обычная карта с обычными условиями)",
                                 fields={
                                     "email": EmailField,
                                     "name": lambda: NameField("name", "Имя", "Введите своё имя",
                                                               vk_field="first_name"),
                                     "phone number": PhoneNumberField,
                                 })

            def admin_description(self):
                return "карта: " + super().admin_description()

        return Card

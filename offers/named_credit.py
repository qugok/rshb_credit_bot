from offer_fields.basic import CreditField
from offer_fields.credit_amount_field import CreditAmountField
from offer_fields.name_field import NameField
from offer_fields.phone_number_field import PhoneNumberField
from offers.offer import Offer


class NamedCredit(Offer):
    description = "Именной кредит, специально для вас!"

    need_vk = True
    vk_fields = "Имя"

    @staticmethod
    def constructor():
        class Credit(CreditField):
            def __init__(self):
                super().__init__(name="credit",
                                 descry="Именной кредит - лучшие проценты!",
                                 fields={
                                     "name": lambda: NameField("name", "Имя", "Введите своё имя", vk_field="first_name"),
                                     "phone number": lambda: PhoneNumberField(default_value="8(800)555-35-35"),
                                     "amount": lambda: CreditAmountField([[50000], [1000000]]),
                                 })

            def admin_description(self):
                return "именной: " + super().admin_description()

        return Credit

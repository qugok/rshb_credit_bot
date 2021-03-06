from offer_fields.age_field import AgeField
from offer_fields.basic import CreditField
from offer_fields.credit_amount_field import CreditAmountField
from offer_fields.name_field import NameField
from offer_fields.phone_number_field import PhoneNumberField
from offers.offer import Offer


class ExpandedCredit(Offer):
    description = "Расширенный кредит, расширяем горизонты!"
    need_vk = True
    vk_fields = "Имя"

    @staticmethod
    def constructor():
        class Credit(CreditField):
            def __init__(self):
                super().__init__(name="credit",
                                 descry="Расширенный кредит - это то, что нужно",
                                 fields={
                                     "name": lambda: NameField("name", "Имя", "Введите своё имя",
                                                               vk_field="first_name"),
                                     "age": AgeField,
                                     "phone number": lambda: PhoneNumberField(default_value="8(800)555-35-35"),
                                     "amount": lambda: CreditAmountField([[50000], [1000000]]),
                                 })

            def admin_description(self):
                return "именной: " + super().admin_description()

        return Credit

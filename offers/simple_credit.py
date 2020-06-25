from offer_fields.basic import CreditField
from offer_fields.credit_amount_field import CreditAmountField
from offer_fields.phone_number_field import PhoneNumberField
from offers.offer import Offer


class SimpleCredit(Offer):
    description = "Простой кредит, для кого угодно!"

    @staticmethod
    def constructor():
        class Credit(CreditField):
            def __init__(self):
                super().__init__(name="credit",
                                 descry="Простой кредит - всё просто!",
                                 fields={
                                     "phone number": PhoneNumberField,
                                     "amount": lambda: CreditAmountField([[5000], [10000]]),
                                 })

            def admin_description(self):
                return "прост: " + super().admin_description()

        return Credit

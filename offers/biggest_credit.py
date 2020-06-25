from offer_fields.basic import CreditField
from offer_fields.credit_amount_field import CreditAmountField
from offer_fields.name_field import NameField
from offer_fields.phone_number_field import PhoneNumberField
from offers.offer import Offer


class BiggestCredit(Offer):
    description = "Не кредит, а Кредитище!"
    need_vk = True
    vk_fields = "Имя, Фамилия, Город, Компания, Должность"

    @staticmethod
    def constructor():
        class Credit(CreditField):
            def __init__(self):
                super().__init__(
                    name="credit",
                    descry="Кредитище - не пожалеешь",
                    fields={
                        "first_name": lambda: NameField("first_name", "Имя", "Введите своё имя", vk_field="first_name"),
                        "second_name": lambda: NameField("second_name", "Фамилия", "Введите свою фамилию",
                                                         vk_field="last_name"),
                        "city": lambda: NameField("city", "Город", "Введите свой город проживания", "Москва",
                                                  vk_field="city"),
                        "company": lambda: NameField("company", "Компания",
                                                     "Введите компанию в которой вы работате", vk_field="career"),
                        "position": lambda: NameField("position", "Должность",
                                                      "Введите должность на которй вы работаете", vk_field="position"),
                        "phone number1": lambda: PhoneNumberField(default_value="8(800)555-35-35"),
                        "amount": lambda: CreditAmountField([[50000], [1000000]]),
                    })

            def fill_from_vk_response(self, response):
                super().fill_from_vk_response(response)
                if "city" in response:
                    self.fields["city"].fill_fields(city=response["city"]["title"])
                if "company_info" in response:
                    if "name" in response["company_info"]:
                        self.fields["company"].fill_fields(company=response["company_info"]["name"])
                    else:
                        self.fields["company"].fill_fields(company=response["company_info"]["company"])
                if "career" in response:
                    self.fields["position"].fill_from_vk_response(response["career"][-1])

            def admin_description(self):
                return "именной: " + super().admin_description()

        return Credit

from offer_fields.primitive_fields import IntCreditField
from offer_fields.basic import CreditField
from messaging.message import Message, MessageType
from offer_fields.phone_number_field import PhoneNumberField
from offer_fields.credit_amount_field import CreditAmountField
from data.offer_reply import OfferReply

def test_int_wanter():
    while 1:
        temp_field = IntCreditField()
        yield from temp_field


def test_wanter_your_number_and_age():
    def age_checker(age: str):
        if not age.isdecimal():
            return (False, "Введите число")
        elif int(age) <= 0:
            return (False, "Вы еще не родились? Введите корректный возраст")
        elif int(age) <= 18:
            return (False, "Вы еще слишком молоды. Позовите совершеннолетнего")
        elif 0 < int(age) < 120:
            return (True, "OK")
        return (False, "Введите корректный возраст")

    age_whanter_constructor = lambda: IntCreditField(name="age",
                                                     descry="Ваш возраст",
                                                     correct_checker=age_checker,
                                                     request="Введите ваш возраст")
    main_whanter = CreditField(fields={"age": age_whanter_constructor, "phone number": PhoneNumberField})

    while 1:
        main_whanter.clear()
        yield from main_whanter


def test_wanter_credit_amount_your_number_and_age(bot):
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

    age_whanter_constructor = lambda: IntCreditField(name="age",
                                                     descry="Ваш возраст",
                                                     correct_checker=age_checker,
                                                     request="Введите ваш возраст")

    main_whanter_constructor = lambda: CreditField(name="credit", descry="кредит 300% годовых с переплатами",
                                                   fields={"amount": lambda: CreditAmountField([[50], [100]]),
                                                           "age": age_whanter_constructor,
                                                           "phone number": PhoneNumberField})
    main_whanter = main_whanter_constructor()

    while 1:
        main_whanter.clear()
        yield from main_whanter

        update = yield Message("Спасибо, что оформили заявку на кредит", "Вот ваша заявка:\n" + str(main_whanter),
                               message_type=MessageType.not_require_response)

        cr = OfferReply(update.message.chat.id, main_whanter.get_info(), main_whanter_constructor)
        bd.reply_to_approve_queue.append(cr.get_address())
        yield Message("Можете оформить ещё одну)").make_keyboard([["Новая заявка"]])

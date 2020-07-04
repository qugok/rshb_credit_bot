from messaging.message import Message, MessageType
from data.offer_reply import OfferReply
from static_info import VK_TOKEN
from vk_utils.wrapper import VKWrapper


class Generators:

    def __init__(self, offer_list, notifier, bd):
        self.bd = bd
        self.notifier = notifier
        self.offer_list = offer_list

    def admin_generator(self):
        while 1:
            yield Message("Здравствуйте, администратор").make_inline_keyboard(
                [[("Ожидают рассмотрения", "admin_check_replies")],
                 [("Одобренные", "admin_approved_replies")],
                 [("Отклонённые", "admin_rejected_replies")],
                 [("Отменённые","admin_cancelled_replies")]])


    def user_default_generator(self):
        yield None
        yield Message("Здравствуйте, пользователь"). \
            make_inline_keyboard([[("Список предложений", "offer_list")], [("Мои заявки", "request_list")]])


    def credit_filling(self, credit_ind):
        vk = VKWrapper(VK_TOKEN)

        yield None
        credit_constructor = self.offer_list[credit_ind].constructor()

        yield Message("Вы всегда можете отменить заполнение заявки командой /menu",
                      message_type=MessageType.not_require_response)

        credit = credit_constructor()

        if self.offer_list[credit_ind].need_vk:
            contin = "Продолжить"
            update = yield Message(
                f'Чтобы не вводить всю информацию Вы можете ввести ссылку(или просто screen name) на свой VK аккаунт, '
                f'чтобы некоторые поля ({self.offer_list[credit_ind].vk_fields})'
                f' заполнились автоматически - её можно получить пройдя по vk.com/id0 и скопировав адрес страницы\n'
                f'Или продолжить').make_keyboard(
                [[contin]])
            if update.message.text != contin:
                fields = credit.get_fields_for_vk()
                try:
                    response = vk.get_user_info(update.message.text, fields)
                    credit.fill_from_vk_response(response)
                except:
                    pass

        yield from credit

        update = yield Message("Спасибо, что оформили заявку на кредит", "Вот ваша заявка:\n" + str(credit),
                               message_type=MessageType.not_require_response)
        cr = OfferReply(update.message.chat.id, credit.get_info(), credit_ind)
        self.bd.write_reply(cr)
        self.bd.flush()
        self.bd.reply_to_approve_queue.append(cr.get_address())
        self.notifier.notify()

        yield Message("Куда дальше?").make_inline_keyboard([[("<<Назад", "main_menu")]])


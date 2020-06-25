from enum import Enum

from offers.offer_list import offer_list


class ReplyStatus(int, Enum):
    Approved = 0
    Rejected = 1
    Pending = 2
    Deleted = 3

    def readable(self):
        if self == ReplyStatus.Approved:
            return "Одобрено"
        if self == ReplyStatus.Rejected:
            return "Отклонено"
        if self == ReplyStatus.Pending:
            return "На рассмотрении"
        if self == ReplyStatus.Deleted:
            return "Удалена"


class OfferReply:
    class Address:
        def __init__(self, chat_id, user_reply_ind):
            self.user_reply_ind = user_reply_ind
            self.chat_id = chat_id

        def __str__(self):
            return f'Address<chat_id = {self.chat_id}, reply_ind = {self.user_reply_ind}'

        def __repr__(self):
            return f'Address<chat_id = {self.chat_id}, reply_ind = {self.user_reply_ind}'

    @staticmethod
    def from_bd_row(credit_data, credit_ind, status, chat_id, row_ind=None):
        return OfferReply(chat_id, credit_data, credit_ind, status, row_ind)

    def __init__(self, chat_id, data, credit_ind, status: ReplyStatus = ReplyStatus.Pending, user_reply_ind=None):
        """

        :param chat_id:
        :param data:
        :param credit_ind: номер кредита из списка, чтобы создать экземпляр
        :param status:
        :param user_reply_ind: номер заявки из списка заявок клиента, если None, то новая
        """
        self.user_reply_ind = user_reply_ind
        self.data = data
        self.credit_ind = credit_ind
        self.status = ReplyStatus(status)
        self.chat_id = chat_id

    def approve(self):
        self.status = ReplyStatus.Approved

    def reject(self):
        self.status = ReplyStatus.Rejected

    def delete(self):
        self.status = ReplyStatus.Deleted

    def is_deleted(self):
        return self.status == ReplyStatus.Deleted

    def __str__(self):
        credit = offer_list[self.credit_ind].constructor()()
        credit.fill_fields(**self.data)
        return str(credit)

    def credit_description(self):
        return offer_list[self.credit_ind].description

    def admin_description(self):
        credit = offer_list[self.credit_ind].constructor()()
        credit.fill_fields(**self.data)
        return credit.admin_description()

    def get_reply(self, is_edited=False, admin=False):
        credit = offer_list[self.credit_ind].constructor()()
        credit.fill_fields(**self.data)
        if admin:
            return ("Заявка:\n") + str(credit) + "\nСтатус:" + self.status.readable()
        return ("Здравствуйте, по вашей заявке:\n" if is_edited else "Ваша заявка:\n") + str(credit) + (
            "\nНовый статус: " if is_edited else "\nСтатус: ") + self.status.readable()

    def get_address(self):
        return OfferReply.Address(self.chat_id, self.user_reply_ind)

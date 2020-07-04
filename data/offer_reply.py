from enum import Enum

from offers.offer_list import offer_list


class ReplyStatus(int, Enum):
    Approved = 0
    Rejected = 1
    Pending = 2
    Cancelled = 3
    Removed = 4

    def readable(self):
        if self == ReplyStatus.Approved:
            return "Одобрено"
        if self == ReplyStatus.Rejected:
            return "Отклонено"
        if self == ReplyStatus.Pending:
            return "На рассмотрении"
        if self == ReplyStatus.Cancelled:
            return "Отменена"
        if self == ReplyStatus.Removed:
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
        self.__user_reply_ind = user_reply_ind
        self.__data = data
        self.__credit_ind = credit_ind
        self.__status = ReplyStatus(status)
        self.__chat_id = chat_id

    def approve(self):
        self.__status = ReplyStatus.Approved

    def reject(self):
        self.__status = ReplyStatus.Rejected

    def cancel(self):
        self.__status = ReplyStatus.Cancelled

    def remove(self):
        self.__status = ReplyStatus.Removed

    def is_removed(self):
        return self.__status == ReplyStatus.Removed

    def is_cancelled(self):
        return self.__status == ReplyStatus.Cancelled

    def __str__(self):
        credit = offer_list[self.__credit_ind].constructor()()
        credit.fill_fields(**self.__data)
        return str(credit)

    def credit_description(self):
        return offer_list[self.__credit_ind].description

    def admin_description(self):
        credit = offer_list[self.__credit_ind].constructor()()
        credit.fill_fields(**self.__data)
        return credit.admin_description()

    def get_reply(self, is_edited=False, admin=False):
        credit = offer_list[self.__credit_ind].constructor()()
        credit.fill_fields(**self.__data)
        if admin:
            return ("Заявка:\n") + str(credit) + "\nСтатус:" + self.__status.readable()
        return ("Здравствуйте, по вашей заявке:\n" if is_edited else "Ваша заявка:\n") + str(credit) + (
            "\nНовый статус: " if is_edited else "\nСтатус: ") + self.__status.readable()

    def get_address(self):
        return OfferReply.Address(self.__chat_id, self.__user_reply_ind)

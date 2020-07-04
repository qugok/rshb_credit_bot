import collections
import json
from json.decoder import JSONDecodeError
from data.offer_reply import ReplyStatus, OfferReply
from static_info import DEFAULT_FILENAME

class JsonDatabase:
    """
    бд в которй хранятся все данные о заявках в формате json
    """

    def __init__(self, filename=DEFAULT_FILENAME):
        self.__filename = filename
        self.__data = collections.defaultdict(list)
        self.reply_to_approve_queue = []

        with open(self.__filename, 'r') as json_file:
            try:
                self.__data.update(json.load(json_file))
            except JSONDecodeError:
                pass

        self.__clear_data_from_deleted()
        self.__fill_reply_queue_from_bd(self.reply_to_approve_queue)

    def get_reply(self, reply_address: OfferReply.Address):
        try:
            reply_data = self.__data[str(reply_address.chat_id)][reply_address.user_reply_ind]
            return OfferReply.from_bd_row(**reply_data, row_ind=reply_address.user_reply_ind)
        except:
            return None

    def get_replies(self, chat_id):
        if str(chat_id) not in self.__data:
            return []
        return self.__data[str(chat_id)]

    def write_reply(self, reply: OfferReply):
        if reply.__user_reply_ind is None:
            reply.__user_reply_ind = self.__add(reply.__chat_id, reply.__status, reply.__credit_ind, reply.__data)
        else:
            self.__update(reply.__chat_id, reply.__status, reply.__credit_ind, reply.__user_reply_ind, reply.__data)

    def __update(self, chat_id, status: ReplyStatus, credit_ind: int, credit_number: int, data):
        self.__data[str(chat_id)][credit_number] = \
            {"credit_data": data, "credit_ind": credit_ind, "status": status,
             "chat_id": chat_id}

    def __add(self, chat_id, status: ReplyStatus, credit_ind: int, data):
        self.__data[str(chat_id)].append(
            {"credit_data": data, "credit_ind": credit_ind, "status": status,
             "chat_id": chat_id})
        return len(self.__data[str(chat_id)]) - 1

    def flush(self):
        with open(self.__filename, 'w+') as outfile:
            json.dump(self.__data, outfile)

    def __fill_reply_queue_from_bd(self, queue: list):
        for chat_id, replies in self.__data.items():
            for ind, reply_data in enumerate(replies):
                if reply_data["status"] == ReplyStatus.Pending:
                    cr = OfferReply.from_bd_row(**reply_data, row_ind=ind)
                    queue.append(cr.get_address())

    def __clear_data_from_deleted(self):
        new_data = collections.defaultdict(list)
        for chat_id, replies in self.__data.items():
            new_data[chat_id] = [reply_data for reply_data in replies if reply_data["status"] != ReplyStatus.Removed]
        self.__data = new_data

    def filter_reply_queue(self):
        self.reply_to_approve_queue = [addr for addr in self.reply_to_approve_queue if
                                       not (self.get_reply(addr).is_deleted() or self.get_reply(addr).is_cancelled())]

    def get_approved_replies(self):
        ret_replies = []
        for chat_id, replies in self.__data.items():
            for ind, reply_data in enumerate(replies):
                if reply_data["status"] == ReplyStatus.Approved:
                    cr = OfferReply.from_bd_row(**reply_data, row_ind=ind)
                    ret_replies.append(cr.get_address())
        return ret_replies

    def get_rejected_replies(self):
        ret_replies = []
        for chat_id, replies in self.__data.items():
            for ind, reply_data in enumerate(replies):
                if reply_data["status"] == ReplyStatus.Rejected:
                    cr = OfferReply.from_bd_row(**reply_data, row_ind=ind)
                    ret_replies.append(cr.get_address())
        return ret_replies

    def get_cancelled_replies(self):
        ret_replies = []
        for chat_id, replies in self.__data.items():
            for ind, reply_data in enumerate(replies):
                if reply_data["status"] == ReplyStatus.Cancelled:
                    cr = OfferReply.from_bd_row(**reply_data, row_ind=ind)
                    ret_replies.append(cr.get_address())
        return ret_replies

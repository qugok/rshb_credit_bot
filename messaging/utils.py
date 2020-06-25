from static_info import TG_MESSAGE_SIZE_LIMIT


def split(message: str):
    temp = ''
    for i in message.split('\n'):
        if len(temp + i) > TG_MESSAGE_SIZE_LIMIT:
            yield temp.strip()
            temp = ''
        temp += '\n' + i
    if len(temp.strip()) != 0:
        yield temp.strip()

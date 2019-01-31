import dbController as dbc


def isMainCommand(dataJson):
    if 'message' in dataJson:
        chat_id = dataJson['message']['chat']['id']
        command = dbc.get_user_answer(chat_id)
        return command is not None
    else:
        return False


def isBotCommand(dataJson):
    if 'message' in dataJson:
        type = dataJson['message']['entities'][0]['type']
        if type == 'bot_command':
            return True
        return False
    return False


def isCallbackQuery(dataJson):
    return 'callback_query' in dataJson

import dbController as dbc


MAIN_COMMANDS = ['розклад', 'пошук викладача', 'профком', 'інше', 'допомога']


def isMainCommand(dataJson):
    if 'message' in dataJson:
        message = dataJson['message']['text'].lower()
        if message in MAIN_COMMANDS:
            return True
        else:
            return False
    return False


def isUserAnswer(dataJson):
    if 'message' in dataJson:
        chat_id = dataJson['message']['chat']['id']
        command = dbc.get_user_answer(chat_id)
        return command is not None
    else:
        return False


def isBotCommand(dataJson):
    if 'message' in dataJson:
        if 'entities' in dataJson['message']:
            type = dataJson['message']['entities'][0]['type']
            if type == 'bot_command':
                return True
            return False
        return False
    return False


def isCallbackQuery(dataJson):
    return 'callback_query' in dataJson

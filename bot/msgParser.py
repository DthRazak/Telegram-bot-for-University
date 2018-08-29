def isBotCommand(dataJson):
    try:
        type = dataJson['message']['entities'][0]['type']
        if type == 'bot_command':
            return True
        return False
    except KeyError:
        return False


def isCallbackQuery(dataJson):
    try:
        return 'callback_query' in dataJson
    except KeyError:
        return False

    return False

def isMainCommand(dataJson):
    try:
        message = dataJson['message']['text']

        if message == 'Розклад' or message == 'розклад' or message == 'timetable':
            return True
        return False

    except KeyError:
        return False

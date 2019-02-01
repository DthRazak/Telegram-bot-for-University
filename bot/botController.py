from datetime import datetime
import requests
import misc.misc
import dbController as dbc
import re
from logger import msg_logger as logger


URL = 'https://api.telegram.org/bot{0}/'.format(misc.misc.token)
emoji = {1: '1\ufe0f\u20e3', 2: '2\ufe0f\u20e3', 3: '3\ufe0f\u20e3', 4: '4\ufe0f\u20e3', 5: '5\ufe0f\u20e3', \
         6: '6\ufe0f\u20e3', 7: '7\ufe0f\u20e3', 8: '8\ufe0f\u20e3', 9: '9\ufe0f\u20e3', 10: '\ud83d\udd1f'}
dayofweek = {'ПН': 'Понеділок', 'ВТ': 'Вівторок', 'СР': 'Середа', 'ЧТ': 'Четвер', 'ПТ': 'П\'ятниця'}
dowENUA = {'Monday': 'ПН', 'Tuesday': 'ВТ', 'Wednesday': 'СР', 'Thursday': 'ЧТ', 'Friday': 'ПТ'}


def sendMessage(chat_id, text, parse_mode='Markdown'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
    r = requests.post(url, json=answer)
    return r.json()


def sendButton(chat_id, text, reply):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text, 'reply_markup': reply }
    r = requests.post(url, json = answer)
    return r.json()


def editCallbackMessage(chat_id, message_id, reply_markup):
    url = URL + 'editMessageReplyMarkup'
    answer = {'chat_id': chat_id, 'message_id': message_id, 'reply_markup': reply_markup}
    r = requests.post(url, json = answer)
    return r.json()


def addKeyboard(chat_id, text, keyboard):
    url = URL + 'sendMessage'
    reply = {'keyboard': keyboard, 'resize_keyboard' : True}
    answer = {'chat_id': chat_id, 'text': text, 'reply_markup': reply}
    r = requests.post(url, json = answer)
    return r.json()


def removeKeyboard(chat_id):
    url = URL + 'sendMessage'
    reply = {'remove_keyboard' : True}
    answer = {'chat_id': chat_id, 'text': 'bye', 'reply_markup': reply}
    r = requests.post(url, json = answer)
    return r.json()


def manageSimpleMessage(dataJson):
    try:
        chat_id = dataJson['message']['chat']['id']
        text = 'Нажаль зараз я не володію штучним інтелектом і тому я не можу відповісти на твоє повідомлення'
        sendMessage(chat_id, text)
    except KeyError:
        try:
            chat_id = dataJson['edited_message']['chat']['id']
            text = 'Спочатку навчись писати без помилок, а потім відправляй мені повідомлення)'
            logMsg = 'editedMessage: chat_id: {0}, message: {1}'.format(chat_id, dataJson['text'])
            logger.warning(logMsg)
            sendMessage(chat_id, text)
        except KeyError:
            logger.error('Some error happened!!!')
            pass


def manageBotCommand(dataJson):
    command = dataJson['message']['text']
    chat_id = dataJson['message']['chat']['id']
    if 'username' in dataJson['message']['chat']:
        username = dataJson['message']['chat']['username']
    else:
        username = 'NULL'

    if command == '/start':
        text = "Привіт, я бот твого улюбленого університету\nЧим я можу тобі допомогти?"
        keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук викладача'}], [{'text': 'Профком'}],
                    [{'text': 'Інше'}, {'text': 'Допомога'}]]
        addKeyboard(chat_id, text, keyboard)
        dbc.register_user(chat_id, username)
    # elif re.search(r'^\/register \w+-\d+$', command):
    #     group = command.split(' ')[1]
    #     try:
    #         username = dataJson['message']['from']['username']
    #     except KeyError:
    #         username = 'NULL'
    #     if not dbc.is_user_registered(chat_id):
    #         if dbc.register_user(chat_id, group, username):
    #             sendMessage(chat_id, 'Реєстрація пройшла успішно')
    #             logMsg = 'User registered chat_id: {0}'.format(chat_id)
    #             logger.info(logMsg)
    #         else:
    #             sendMessage(chat_id, 'Щось пішло не так, спробуйте ще раз')
    #     else:
    #         sendMessage(chat_id, 'Ви вже зареєстровані')
    # elif command == '/deleteme':
    #     if dbc.is_user_registered(chat_id):
    #         dbc.delete_user(chat_id)
    #         sendMessage(chat_id, 'Видалення пройшло успішно')
    #         logMsg = 'User was deleted chat_id: {0}'.format(chat_id)
    #         logger.info(logMsg)
    #     else:
    #         sendMessage(chat_id, 'Ви ще не були зареєстровані')
    else:
        text = "Нажаль я не розумію такої команди("
        sendMessage(chat_id, text)


def manageMainComand(dataJson):
    chat_id = dataJson['message']['chat']['id']
    message = dataJson['message']['text'].lower()
    if message == 'розклад':
        rawData = dbc.get_facultets()
        buttons = makeButtons('facultet_', 2, list(rawData.values()))
        sendButton(chat_id, 'Зробіть будь-ласка свій вибір', buttons)
    elif message == 'пошук викладача':
        pass
        # TODO implement this method
    elif message == 'профком':
        pass
        # TODO implement this method to
    elif message == 'інше':
        pass
        # TODO and this)
    elif message == 'допомога':
        text = "Якщо у вас є якісь пропозиції щодо бота, або ви знайшли недостовірну інформацію" \
                " то напишіть мені на електронну пошту dth.razak@gmail.com"
        sendMessage(chat_id, text)


def manageCallbackQuery(dataJson):
    data = dataJson['callback_query']['data']
    chat_id = dataJson['callback_query']['message']['chat']['id']
    message_id = dataJson['callback_query']['message']['message_id']

    # Захоплення факультетів, надсилання курсів
    if re.search('facultet_\w+', data):
        callbackText = data.split('_')
        buttons = makeButtons(callbackText[1] + '_course_', 2, ['1', '2', '3', '4', '5', '6', '<< Назад'])
        editCallbackMessage(chat_id, message_id, buttons)

    # Захоплення курсів, надсилання груп
    elif re.search(r'^\w+_course_[1-6]$', data):
        rawData = dbc.get_groups(data.split('_')[0], data[-1])
        groups = []
        for group in rawData:
            groups.append(group)
        groups.append('<< Назад')
        buttons = makeButtons(data + '_', 3, groups)
        editCallbackMessage(chat_id, message_id, buttons)

    # Захоплення груп надсилання дня тижня
    elif re.search(r'^\w+_course_[1-6]_\d+$', data):
        buttons = makeButtons(data + '_', 3, ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', '<< Назад'])
        editCallbackMessage(chat_id, message_id, buttons)

    # Перехід до факультетів з курсів
    elif re.search('course_back', data):
        rawData = dbc.get_facultets()
        buttons = makeButtons('facultet_', 2, list(rawData.values()))
        editCallbackMessage(chat_id, message_id, buttons)

    # Перехід до курсів з груп
    elif re.search(r'^\w+_course_[1-6]_back$', data):
        callbackText = data.split('_')[0]
        buttons = makeButtons(callbackText + '_course_', 2, ['1', '2', '3', '4', '5', '6', '<< Назад'])
        editCallbackMessage(chat_id, message_id, buttons)

    # Перехід з днів тижня до груп
    elif re.search(r'^\w+_course_[1-6]_\d+_back$', data):
        rawData = dbc.get_groups(data.split('_')[0], data.split('_')[2])
        groops = []
        for groop in rawData:
            groops.append(groop)
        groops.append('<< Назад')
        callbackText = data.split('_')[0] + '_' + data.split('_')[1] + '_' + data.split('_')[2] + '_'
        buttons = makeButtons(callbackText, 3, groops)
        editCallbackMessage(chat_id, message_id, buttons)

    elif re.search(r'^\w+_course_[1-6]_\d+_[^b]\w+$', data):
        day = data.split('_')[4]
        group_id = data.split('_')[3]
        group = dbc.get_group_by_id(group_id)
        try:
            username = dataJson['callback_query']['message']['chat']['username']
        except KeyError:
            username = ''
        logMsg = 'Timetable for {0} {1}, group: {2}'.format(username, chat_id, group)
        logger.info(logMsg)
        sendTimetable(chat_id, day, group_id)
    else:
        logMsg = 'Undefined behaviour for callback query({0})'.format(data)
        logger.error(logMsg)


def sendTimetable(chat_id, day, group_id, daily=False):
    data = dbc.get_timetable(day, group_id)
    group = dbc.get_group_by_id(group_id)
    text = ''
    if not data == []:
        text = '\t**{0}**\t {1}'.format(dayofweek[day], group)
    else:
        text = 'Нажаль розклад відсутній у базі даних 😔'
    prev_row = (0, '', '')
    for row in data:
        num, subj_name, auditory, class_type, alternation, lector = row

        number = emoji[row[0]]

        if prev_row == (num, subj_name, auditory):
            text = text + ', ' + lector
            continue

        prev_row = (num, subj_name, auditory)

        if auditory is not None:
            auditory = ' ' + auditory + ' ауд.'
        else:
            auditory = ''

        if alternation is not None:
            alternation = '(' + row[-1] + ')'
        else:
            alternation = ''

        if lector is not None:
            lector = '\n' + lector
        else:
            lector = ''

        if not daily:
            text = text + '\n\n{0} пара - {1}, {2} {3} {4} {5}'\
                .format(number, subj_name, class_type, auditory, alternation, lector)
        else:
            d = datetime.now()
            if d.isocalendar()[1] % 2 == 1 and alternation == '(чисельник)':
                pass
            elif d.isocalendar()[1] % 2 == 0 and alternation == '(знаменник)':
                pass
            else:
                text = text + '\n\n{0} пара - {1}, {2} {3} {4} {5}' \
                    .format(number, subj_name, class_type, auditory, alternation, lector)

    sendMessage(chat_id, text)


def makeButtons(callbackText='', number=3, buttonsArray=[]):
    arrays = []
    array = []
    while buttonsArray.__len__() > 0:
        text = buttonsArray[0]
        #Відповідь для вибраного факультету
        if callbackText == 'facultet_':
            callbackData = callbackText + dbc.get_facultet_id(buttonsArray[0])

        #Відповідь для вибраного курсу
        elif re.search(r'^\w+_course_$', callbackText):
            text = buttonsArray[0] + ' курс'
            callbackData = callbackText + buttonsArray[0]
            if buttonsArray[0] == '<< Назад':
                callbackData = 'course_back'
                text = '<< Назад'

        #Відповідь для вибраної групи
        elif re.search(r'^\w+_course_[1-6]_$', callbackText):
            callbackData = callbackText + str(dbc.get_group_id(text))
            if text == '<< Назад':
                callbackData = callbackText + 'back'

        #Відповідь для вибраного дня тижня
        elif re.search(r'^\w+_course_[1-6]_\d+_$', callbackText):
            callbackData = callbackText + text
            if text == '<< Назад':
                callbackData = callbackText + 'back'

        else:
            callbackData = str(callbackText) + str(buttonsArray[0])
            if text == '<< Назад':
                callbackData = callbackText + 'back'


        array.append({'text': text, 'callback_data': callbackData})
        buttonsArray.pop(0)
        if array.__len__() == number:
            arrays.append(array)
            array = []
    if array.__len__() > 0:
        arrays.append(array)

    reply = {'inline_keyboard': arrays}
    return reply


def sendDailyTimetable():
    d = datetime.now()
    if d.strftime('%A') in dowENUA:
        users = dbc.get_users()
        for user in users:
            sendTimetable(user[1], dowENUA[d.strftime('%A')], user[2], daily = True)

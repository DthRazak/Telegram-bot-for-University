from datetime import datetime
import requests
import misc.misc
import dbController
import re

URL = 'https://api.telegram.org/bot{0}/'.format(misc.misc.token)
emoji = {1: '1\ufe0f\u20e3', 2: '2\ufe0f\u20e3', 3: '3\ufe0f\u20e3', 4: '4\ufe0f\u20e3', 5: '5\ufe0f\u20e3', \
         6: '6\ufe0f\u20e3', 7: '7\ufe0f\u20e3', 8: '8\ufe0f\u20e3', 9: '9\ufe0f\u20e3', 10: '\ud83d\udd1f'}
dayofweek = {'ПН': 'Понеділок', 'ВТ': 'Вівторок', 'СР': 'Середа', 'ЧТ': 'Четвер', 'ПТ': 'П\'ятниця'}


def sendMessage(chat_id, text, parse_mode = 'Markdown'):
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


def manageSimpleMeassage(dataJson):
    chat_id = dataJson['message']['chat']['id']
    text = 'Нажаль зараз я не володію штучним інтелектом і тому я не можу відповісти на твоє повідомлення'
    sendMessage(chat_id, text)


def manageBotCommand(dataJson):
    command = dataJson['message']['text']
    chat_id = dataJson['message']['chat']['id']
    if command == '/start':
        text = "Привіт, я бот твого улюбленого університету\nЧим я можу тобі допомогти?"
        addKeyboard(chat_id, text, 'Розклад')
    elif command == '/support':
        text = "Якщо в тебе є якісь пропозиції щодо бота, або ти знайшов недостовірну інформацію \
        то напиши мені на електронну пошту dth.razak@gmail.com"
        sendMessage(chat_id, text)
    else:
        text = "Нажаль я не розумію такої команди("
        sendMessage(chat_id, text)


def manageMainComand(dataJson):
    chat_id = dataJson['message']['chat']['id']
    message = dataJson['message']['text']
    if message == 'Розклад' or message == 'розклад' or message == 'timetable':
        rawData = dbController.getFacultets()
        facultets = []
        for facultet in rawData:
            facultets.append(facultet[0])
        buttons = makeButtons('facultet_', 2, facultets)
        sendButton(chat_id, 'Зроби будь-ласка свій вибір', buttons)


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
    elif re.search(r'^\w+_course_[1-4]$', data):
        rawData = dbController.getGroops(data.split('_')[0], data[-1])
        groops = []
        for groop in rawData:
            groops.append(groop[0])
        groops.append('<< Назад')
        buttons = makeButtons(data + '_', 3, groops)
        editCallbackMessage(chat_id, message_id, buttons)

    # Захоплення груп надсилання дня тижня
    elif re.search(r'^\w+_course_[1-4]_[^b]\w+-\d+$', data):
        buttons = makeButtons(data + '_', 3, ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', '<< Назад'])
        editCallbackMessage(chat_id, message_id, buttons)

    # Перехід до факультетів з курсів
    elif re.search('course_back', data):
        rawData = dbController.getFacultets()
        facultets = []
        for facultet in rawData:
            facultets.append(facultet[0])
        buttons = makeButtons('facultet_', 2, facultets)
        editCallbackMessage(chat_id, message_id, buttons)

    # Перехід до курсів з груп
    elif re.search(r'^\w+_course_[1-4]_back$', data):
        callbackText = data.split('_')[0]
        buttons = makeButtons(callbackText + '_course_', 2, ['1', '2', '3', '4', '<< Назад'])
        editCallbackMessage(chat_id, message_id, buttons)

    # Перехід з днів тижня до груп
    elif re.search(r'^\w+_course_[1-4]_[^b]\w+-\d+_back$', data):
        rawData = dbController.getGroops(data.split('_')[0], data.split('_')[2])
        groops = []
        for groop in rawData:
            groops.append(groop[0])
        groops.append('<< Назад')
        callbackText = data.split('_')[0] + '_' + data.split('_')[1] + '_' + data.split('_')[2] + '_'
        buttons = makeButtons(callbackText, 3, groops)
        editCallbackMessage(chat_id, message_id, buttons)

    else:
        day = data.split('_')[4]
        group = data.split('_')[3]
        sendTimetable(chat_id, day, group)


def sendTimetable(chat_id, day, group):
    data = dbController.getTimetable(day, group)
    text = '\t**{0}**\n\n'.format(dayofweek[day])
    for row in data:
        if row[4] == 'practic':
            type = 'практична'
        else:
            type = 'лекція'

        if not row[2] == None:
            auditory = ' ' + str(row[2]) + ' ауд.'
        else:
            auditory = ''

        if not row[-1] == None:
            alternation = '(' + row[-1] + ')'
            d = datetime.now()
            if d.isocalendar()[1] // 2 == 0 and alternation == '(чисельник)':
                alternation = '**{0}**'.format(alternation)
            elif d.isocalendar()[1] // 2 == 1 and alternation == '(знаменник)':
                alternation = '**{0}**'.format(alternation)
        else:
            alternation = ''
        number = emoji[row[0]]
        text = text + '{0} пара - {1}, {2} {3} {4}\n\n'.format(number, row[1], type, auditory, alternation)
    sendMessage(chat_id, text)


def makeButtons(callbackText = '', number = 3, buttonsArray = []):
    arrays = []
    array = []
    while buttonsArray.__len__() > 0:
        #Відповідь для вибраного факультету
        if callbackText == 'facultet_':
            callbackData = callbackText + dbController.getShortFacultetName(buttonsArray[0])
            text = buttonsArray[0]

        #Відповідь для вибраного курсу
        elif re.search(r'^\w+_course_$', callbackText):
            text = buttonsArray[0] + ' курс'
            callbackData = callbackText + buttonsArray[0]
            if buttonsArray[0] == '<< Назад':
                callbackData = 'course_back'
                text = '<< Назад'

        #Відповідь для вибраної групи
        elif re.search(r'^\w+_course_[1-4]_$', callbackText):
            text = buttonsArray[0]
            callbackData = callbackText + buttonsArray[0]
            if buttonsArray[0] == '<< Назад':
                callbackData = callbackText + 'back'

        #Відповідь для вибраного дня тижня
        elif re.search(r'^\w+_course_[1-4]_[^b]\w+-\d+_$', callbackText):
            text = buttonsArray[0]
            callbackData = callbackText + buttonsArray[0]
            if buttonsArray[0] == '<< Назад':
                callbackData = callbackText + 'back'

        else:
            text = buttonsArray[0]
            callbackData = str(callbackText) + str(buttonsArray[0])
            if buttonsArray[0] == '<< Назад':
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


def addKeyboard(chat_id, text, title):
    url = URL + 'sendMessage'
    reply = {'text': title}
    array = [[reply,], ]
    reply = {'keyboard': array, 'resize_keyboard' : True}
    answer = {'chat_id': chat_id, 'text': text, 'reply_markup': reply}
    r = requests.post(url, json = answer)
    return r.json()


def removeKeyboard(chat_id):
    url = URL + 'sendMessage'
    reply = {'remove_keyboard' : True}
    answer = {'chat_id': chat_id, 'text': 'bye', 'reply_markup': reply}
    r = requests.post(url, json = answer)
    return r.json()

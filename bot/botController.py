from datetime import datetime
import requests
import misc.misc
import dbController as dbc
import re
import random
from logger import msg_logger as logger


URL = 'https://api.telegram.org/bot{0}/'.format(misc.misc.token)
emoji = {1: '1\ufe0f\u20e3', 2: '2\ufe0f\u20e3', 3: '3\ufe0f\u20e3', 4: '4\ufe0f\u20e3', 5: '5\ufe0f\u20e3', \
         6: '6\ufe0f\u20e3', 7: '7\ufe0f\u20e3', 8: '8\ufe0f\u20e3', 9: '9\ufe0f\u20e3', 10: '\ud83d\udd1f'}
randEmoji = ['\ud83d\ude02', '\ud83d\ude0d', '\ud83d\ude18', '\ud83d\ude0a', '\ud83d\ude01', '\ud83d\ude2d',
             '\ud83d\ude1c', '\ud83d\ude33', '\ud83d\ude12', '\ud83d\ude14', '\ud83d\ude09', '\ud83d\ude0f',
             '\ud83d\ude1d', '\ud83d\ude00', '\ud83d\ude10', '\ud83d\ude07','\ud83d\ude06', '\ud83d\ude0b',
             '\ud83e\udd28', '\ud83d\ude0e', '\ud83e\udd2a', '\ud83d\ude31', '\ud83e\udd2c', '\ud83d\ude13']
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


def maintenance(dataJson):
    if 'message' in dataJson:
        chat_id = dataJson['message']['chat']['id']
    elif 'edited_message' in dataJson:
        chat_id = dataJson['edited_message']['chat']['id']
    elif 'callback_query':
        chat_id = dataJson['callback_query']['message']['chat']['id']
    else:
        chat_id = None
    if chat_id is not None:
        sendMessage(chat_id, 'Бот на обслуговуванні, спробуйте пізніше')


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
        keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук'}],
                    [{'text': 'Інше'}, {'text': 'Допомога'}]]
        addKeyboard(chat_id, text, keyboard)
        dbc.register_user(chat_id, username)
    elif command == '/keyboard':
        keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук'}],
                    [{'text': 'Інше'}, {'text': 'Допомога'}]]
        addKeyboard(chat_id, random.choice(randEmoji), keyboard)
        dbc.set_user_answer(chat_id, 'NULL')
    elif command == '/help':
        text = "Якщо у вас є якісь пропозиції щодо бота, або ви знайшли недостовірну інформацію" \
               " то напишіть мені на електронну пошту dth.razak@gmail.com\n" \
               "Щоб повернути клавіатуру відправте /keyboard"
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
    elif message == 'пошук':
        dbc.set_user_answer(chat_id, '\"find\"')
        keyboard = [[{'text': 'Викладач'}, {'text': 'Аудиторія'}], [{'text': '<< Назад'}]]
        addKeyboard(chat_id, random.choice(randEmoji), keyboard)
    elif message == 'пошук викладача':
        dbc.set_user_answer(chat_id, '\"find_lector\"')
        keyboard = [[{'text': '<< Назад'}]]
        text = 'Введіть день тижня та ПІБ викладача\n' \
               'Наприклад: СР Музичук А. О.'
        addKeyboard(chat_id, text, keyboard)
    elif message == 'профком':
        dbc.set_user_answer(chat_id, '\"ppos\"')
        keyboard = [[{'text': 'Новини'}], [{'text': 'Питання / Відповідь'}], [{'text': '<< Назад'}]]
        addKeyboard(chat_id, random.choice(randEmoji), keyboard)
    elif message == 'інше':
        dbc.set_user_answer(chat_id, '\"other\"')
        sub = 'Підписатися' if not dbc.is_user_subscribed(chat_id) else 'Відписатися'
        keyboard = [[{'text': sub}], [{'text': 'Співпраця'}], [{'text': '<< Назад'}]]
        addKeyboard(chat_id, random.choice(randEmoji), keyboard)
    elif message == 'допомога':
        text = "Якщо у вас є якісь пропозиції щодо бота, або ви знайшли недостовірну інформацію" \
                " то напишіть мені на електронну пошту dth.razak@gmail.com"
        sendMessage(chat_id, text)


def manageUserAnswer(dataJson):
    chat_id = dataJson['message']['chat']['id']
    message = dataJson['message']['text'].lower()
    answer = dbc.get_user_answer(chat_id)

    if answer == 'other':
        if message == 'підписатися' and not dbc.is_user_subscribed(chat_id):
            text = 'Введіть будь ласка свою групу:'
            keyboard = [[{'text': '<< Назад'}]]
            addKeyboard(chat_id, text, keyboard)
            dbc.set_user_answer(chat_id, '\"group_sub\"')
        elif message == 'відписатися' and dbc.is_user_subscribed(chat_id):
            dbc.unsubscribe(chat_id)
            text = 'Ви відписалися від розсилки розкладу \ud83d\ude23'
            keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук'}],
                        [{'text': 'Інше'}, {'text': 'Допомога'}]]
            addKeyboard(chat_id, text, keyboard)
            dbc.set_user_answer(chat_id, 'NULL')
        elif message == 'співпраця':
            text = 'Ваш код: {0}'.format(dbc.get_user_code(chat_id))
            keyboard = [[{'text': 'Інформація по співпраці', 'url': misc.misc.sub_url}]]
            reply = {'inline_keyboard': keyboard}
            sendButton(chat_id, text, reply)
        elif message == '<< назад':
            keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук'}],
                        [{'text': 'Інше'}, {'text': 'Допомога'}]]
            addKeyboard(chat_id, random.choice(randEmoji), keyboard)
            dbc.set_user_answer(chat_id, 'NULL')
        else:
            text = 'Я вас не зрозумів, спробуйте ще раз'
            sendMessage(chat_id, text)
    elif answer == 'group_sub':
        if re.search(r'^\w{3}-\d{2}$', message):
            group_id = dbc.get_group_id(message.upper())
            if group_id is not None:
                dbc.subscribe(chat_id, group_id)
                keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук'}],
                            [{'text': 'Інше'}, {'text': 'Допомога'}]]
                text = 'Ви підписалися на розсилку розкладу👍 \ud83d\udc4d'
                addKeyboard(chat_id, text, keyboard)
                dbc.set_user_answer(chat_id, 'NULL')
            else:
                text = 'Нажаль така група відсутня у базі даних, спробуйте ще раз або загляніть у підпункт співпраця'
                sendMessage(chat_id, text)
        elif message == '<< назад':
            dbc.set_user_answer(chat_id, '\"other\"')
            sub = 'Підписатися' if dbc.is_user_subscribed(chat_id) else 'Відписатися'
            keyboard = [[{'text': sub}], [{'text': 'Співпраця'}], [{'text': '<< Назад'}]]
            addKeyboard(chat_id, random.choice(randEmoji), keyboard)
        else:
            text = 'Я вас не зрозумів, спробуйте ще раз'
            sendMessage(chat_id, text)
    elif answer == 'find':
        if message == 'викладач':
            dbc.set_user_answer(chat_id, '\"find_lector\"')
            keyboard = [[{'text': '<< Назад'}]]
            text = 'Введіть день тижня та ПІБ викладача\n' \
                   'Наприклад: СР Музичук А. О.'
            addKeyboard(chat_id, text, keyboard)
        elif message == 'аудиторія':
            dbc.set_user_answer(chat_id, '\"find_auditory\"')
            keyboard = [[{'text': '<< Назад'}]]
            text = 'Введіть день тижня та групу\n' \
                   'Наприклад: ЧТ 439'
            addKeyboard(chat_id, text, keyboard)
        elif message == '<< назад':
            keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук'}],
                        [{'text': 'Інше'}, {'text': 'Допомога'}]]
            addKeyboard(chat_id, random.choice(randEmoji), keyboard)
            dbc.set_user_answer(chat_id, 'NULL')
        else:
            text = 'Я вас не зрозумів, спробуйте ще раз'
            sendMessage(chat_id, text)
    elif answer == 'find_lector':
        if not message == '<< назад':
            arr = message.split(' ', maxsplit=1)
            if len(arr) > 1:
                day = arr[0].upper()
                lector = arr[1].title()
                if day in dayofweek.keys():
                    data = dbc.find_lector(lector, day)
                    if not data == []:
                        text = '\t**{0}**\t {1}\n\n'.format(dayofweek[day], lector)
                        for row in data:
                            number, auditory = row

                            number = emoji[number]

                            if auditory is not None:
                                auditory = ' ' + auditory + ' ауд.'
                            else:
                                auditory = '?'

                            text = text + '{0} пара - {1}\n\n'.format(number, auditory)
                    else:
                        text = 'Нажаль така інформація відсутня у базі даних'
                else:
                    text = 'Не коректно введено день тижня, спробуйте ще раз'
            else:
                text = 'Не коректне введення, спробуйте ще раз'
            sendMessage(chat_id, text)
        else:
            dbc.set_user_answer(chat_id, '\"find\"')
            keyboard = [[{'text': 'Викладач'}, {'text': 'Аудиторія'}], [{'text': '<< Назад'}]]
            addKeyboard(chat_id, random.choice(randEmoji), keyboard)
    elif answer == 'find_auditory':
        if not message == '<< назад':
            arr = message.split(' ', maxsplit=1)
            if len(arr) > 1:
                day = arr[0].upper()
                auditory = arr[1].lower()
                if day in dayofweek.keys():
                    text = '\t**{0}**\t {1} ауд.'.format(dayofweek[day], auditory)
                    data = dbc.find_groups_by_auditory(auditory, day)
                    if not data == []:
                        prev_num = 0
                        for row in data:
                            number, group = row
                            if prev_num == number:
                                text = text + ', {0}'.format(group)
                            else:
                                text = text + '\n\n{0} пара - {1}'.format(emoji[number], group)
                            prev_num = number
                        text = text + "\n\nPS. Інформація надана для аудиторій незалежно від корпусу."
                    else:
                        text = 'Нажаль така інформація відсутня у базі даних'
                else:
                    text = 'Не коректно введено день тижня, спробуйте ще раз'
            else:
                text = 'Не коректне введення, спробуйте ще раз'
            sendMessage(chat_id, text)
        else:
            dbc.set_user_answer(chat_id, '\"find\"')
            keyboard = [[{'text': 'Викладач'}, {'text': 'Аудиторія'}], [{'text': '<< Назад'}]]
            addKeyboard(chat_id, random.choice(randEmoji), keyboard)
    elif answer == 'ppos':
        if message == 'новини':
            text = 'Ця функціональність незабаром з\'явиться'
            sendMessage(chat_id, text)
        elif message == 'питання / відповідь':
            text = 'Ця функціональність незабаром з\'явиться'
            sendMessage(chat_id, text)
        elif message == '<< назад':
            keyboard = [[{'text': 'Розклад'}], [{'text': 'Пошук викладача'}],
                        [{'text': 'Інше'}, {'text': 'Допомога'}]]
            addKeyboard(chat_id, random.choice(randEmoji), keyboard)
            dbc.set_user_answer(chat_id, 'NULL')
        else:
            text = 'Я вас не зрозумів, спробуйте ще раз'
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
        text = '\t*{0}*\t {1}'.format(dayofweek[day], group)
    else:
        text = 'Нажаль розклад відсутній у базі даних 😔'
    prev_row = (0, '', '')
    for row in data:
        num, subj_name, auditory, class_type, alternation, lector = row

        number = emoji[row[0]]

        if prev_row == (num, subj_name, auditory):
            text = text + ', ' + lector
            continue

        if auditory is not None:
            auditory_name = ' *' + auditory + '* ауд.'
        else:
            auditory_name = ''

        if alternation is not None:
            alternation = '(' + alternation + ')'
        else:
            alternation = ''

        if lector is None:
            lector = ''

        if not daily:
            if not num == prev_row[0]:
                text = text + '\n\n{0} пара - {1}, {2} {3} {4} {5}'\
                    .format(number, subj_name, class_type, auditory_name, alternation, lector)
            else:
                text = text + ', {0} {1}'.format(auditory_name, lector)
        else:
            d = datetime.now()
            if d.isocalendar()[1] % 2 == 1 and alternation == '(чисельник)':
                pass
            elif d.isocalendar()[1] % 2 == 0 and alternation == '(знаменник)':
                pass
            else:
                if not num == prev_row[0]:
                    text = text + '\n\n{0} пара - {1}, {2} {3} {4} {5}' \
                        .format(number, subj_name, class_type, auditory_name, alternation, lector)
                else:
                    text = text + ', {0} {1}'.format(auditory_name, lector)

        prev_row = (num, subj_name, auditory)

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
        users = dbc.get_sub_users()
        for user in users:
            sendTimetable(user[0], dowENUA[d.strftime('%A')], user[1], daily = True)

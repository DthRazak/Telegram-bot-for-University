import sqlite3
import os
path = os.path.abspath(os.path.dirname(__file__))
conn = sqlite3.connect(path + '/database/database.db', check_same_thread=False)
c = conn.cursor()

def getTimetable(day, group):
    timetable = []
    sql = 'SELECT * FROM timetable WHERE (studing_day = \'{0}\') and (studing_group = \'{1}\') ORDER BY number'.format(day, group)
    for row in c.execute(sql):
        timetable.append(row)
    return timetable


def getGroops(facultet, course):
    groops = []
    sql = 'SELECT * FROM studing_group WHERE (name LIKE \'___-{0}_\') and (facultet = \'{1}\') ORDER BY name;'.format(course, facultet)
    for row in c.execute(sql):
        groops.append(row)
    return groops


def getFacultets():
    facultets = []
    sql = 'SELECT name FROM facultets'
    for row in c.execute(sql):
        facultets.append(row)
    return facultets


def getShortFacultetName(name):
    sql = 'SELECT short_name FROM facultets WHERE name = \'{0}\''.format(name)
    c.execute(sql)
    return c.fetchall()[0][0]


def registerUser(chat_id, group, username = 'NULL'):
    if not username == 'NULL':
        sql = 'INSERT INTO users (chat_id, studing_group, username) VALUES ({0}, \'{1}\', \'{2}\')'.format(chat_id, group, username)
    else:
        sql = 'INSERT INTO users (chat_id, studing_group, username) VALUES ({0}, \'{1}\', {2})'.format(chat_id, group, username)
    try:
        c.execute(sql)
        conn.commit()
    except sqlite3.IntegrityError:
        return False

    return True


def deleteUser(chat_id):
    sql = 'DELETE FROM users WHERE chat_id = {0}'.format(chat_id)
    c.execute(sql)
    conn.commit()


def isUserRegistered(chat_id):
    sql = 'SELECT * FROM users WHERE chat_id = {0}'.format(chat_id)
    c.execute(sql)
    if not c.fetchone() == None:
        return True
    else:
        return False


def getUsers():
    sql = 'SELECT * FROM users'
    users = []
    for row in c.execute(sql):
        users.append(row)
    return users

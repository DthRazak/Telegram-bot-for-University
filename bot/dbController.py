import sqlite3
import os
path = os.path.abspath(os.path.dirname(__file__))
conn = sqlite3.connect(path + '/database/database.db', check_same_thread=False)
c = conn.cursor()

def getTimetable(day, group):
    timetable = []
    sql = 'SELECT * FROM timetable WHERE (studing_day = \'{0}\') and (studing_group = \'{1}\')'.format(day, group)
    for row in c.execute(sql):
        timetable.append(row)
    return timetable


def getGroops(facultet, course):
    groops = []
    sql = 'SELECT * FROM studing_group WHERE (name LIKE \'___-{0}_\') and (facultet = \'{1}\');'.format(course, facultet)
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
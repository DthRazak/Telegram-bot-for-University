import sqlite3
import pandas as pd
import os
from logger import db_logger as logger


path = os.path.abspath(os.path.dirname(__file__))
conn = sqlite3.connect(path + '/database/database.db', check_same_thread=False)
c = conn.cursor()


def get_timetable(day, group):
    timetable = list()
    sql = """
    SELECT
        number,
        subjects.name as subj_name,
        auditory,
        classes_type,
        alternation,
        lectors.name as lector_name
    FROM
        timetable
        INNER JOIN classes ON classes.c_id = timetable.class_id
        INNER JOIN lectors_subjects_composite ON lectors_subjects_composite.c_id = timetable.class_id
        INNER JOIN lectors ON lectors.l_id = lectors_subjects_composite.l_id
        INNER JOIN subjects ON subjects.s_id = lectors_subjects_composite.s_id
    WHERE
        (group_id = {0}) and (day = \"{1}\");""".format(group, day)
    for row in c.execute(sql):
        timetable.append(row)
    return timetable


def get_groups(facultet, course):
    groups = list()
    sql = 'SELECT name, group_id FROM groups WHERE (name LIKE \'___-{0}%\') and (facultet = \'{1}\') ORDER BY name;'\
        .format(course, facultet)
    for row in c.execute(sql):
        groups.append(row)
    return groups


def get_group_id(name):
    sql = "SELECT group_id FROM groups WHERE name = \"{0}\"".format(name)
    row = c.execute(sql).fetchone()
    if row is not None:
        return row[0]
    return None


def get_facultets():
    facultets = list()
    sql = 'SELECT f_id, name FROM facultets'
    for row in c.execute(sql):
        facultets.append(row)
    return dict(facultets)


def find_lector(name, day):
    l_id = get_lector_id(name)
    if l_id is None:
        return []
    sql = """
    SELECT
        number,
        auditory
    FROM
        classes
        INNER JOIN (SELECT * FROM lectors_subjects_composite WHERE l_id = {0}) lsc 
            ON classes.c_id = lsc.c_id
    WHERE day = \"{1}\"""".format(l_id, day)
    timetable = list()
    for row in c.execute(sql):
        timetable.append(row)
    return timetable


def get_lectors(name):
    lectors = list()
    sql = 'SELECT l_id, name FROM lectors ' \
          'WHERE (name LIKE \'{0} %\') or (name = \'{0}\') ORDER BY name'.format(name)
    for row in c.execute(sql):
        lectors.append(row)
    return lectors


def get_lector_id(name):
    if name is not None:
        sql = "SELECT l_id FROM lectors WHERE name = \"{0}\"".format(name)
        row = c.execute(sql).fetchone()
        if row is not None:
            return row[0]
    return None


def get_subject_id(name):
    sql = "SELECT s_id FROM subjects WHERE name = \"{0}\"".format(name)
    row = c.execute(sql).fetchone()
    if row is not None:
        return row[0]
    return None


def add_subject(name):
    sql = "INSERT INTO subjects (name) VALUES (\"{0}\")".format(name)
    c.execute(sql)
    conn.commit()
    log_msg = 'New subject added ({0})'.format(name)
    logger.info(log_msg)


def add_lector(name):
    sql = "INSERT INTO lectors (name) VALUES (\"{0}\")"\
        .format(name)
    c.execute(sql)
    conn.commit()
    log_msg = 'New lector ({0})'.format(name)
    logger.info(log_msg)


def add_group(name, facultet_id):
    if facultet_id not in get_facultets():
        raise ValueError("Facultet id doesn't exist!")
    sql = "INSERT INTO groups (name, facultet) VALUES (\"{0}\", \"{1}\");".format(name, facultet_id)
    c.execute(sql)
    conn.commit()
    log_msg = 'New group ({0}) added'.format(name)
    logger.info(log_msg)


def add_class(number, day, classes_type, auditory, alternation):
    assert number in range(1, 9)
    assert day in ("ПН", "ВТ", "СР", "ЧТ", "ПТ")
    alternation = '\"' + alternation + '\"' if len(alternation) > 0 else 'NULL'
    auditory = '\"' + auditory + '\"' if len(auditory) > 0 else 'NULL'
    sql = "INSERT INTO classes (number, day, auditory, classes_type, alternation) " \
          "VALUES ({0}, \"{1}\", {2}, \"{3}\", {4})"\
        .format(number, day, auditory, classes_type, alternation)
    c.execute(sql)
    conn.commit()


def add_lectors_subjects_composite(subject_id, class_id, lectors_id):
    for l_id in lectors_id:
        sql = "INSERT INTO lectors_subjects_composite (l_id, s_id, c_id) VALUES ({0}, {1}, {2})" \
            .format(l_id, subject_id, class_id)
        c.execute(sql)
        conn.commit()


def add_timetable(group_id, class_id):
    sql = "INSERT INTO timetable (group_id, class_id) VALUES ({0}, {1})".format(group_id, class_id)
    c.execute(sql)
    conn.commit()


def read_csv(filename):
    return pd.read_csv(filename, sep=';', dtype={'auditory': object, 'alternation': object}, keep_default_na=False)


# if all data is correct
def write_single_record(group, day, number, subject_name, class_type, auditory='', alternation='', lectors=[]):
    group_id = get_group_id(group)
    subject_id = get_subject_id(subject_name)
    lectors_id = [get_lector_id(l) for l in lectors]
    add_class(number, day, class_type, auditory, alternation)
    class_id = c.lastrowid  # weak method
    add_lectors_subjects_composite(subject_id, class_id, lectors_id)
    add_timetable(group_id, class_id)


# groups must be in database
def write_timetable(data):
    for subject in data['subject_name'].unique():
        if get_subject_id(subject) is None:
            add_subject(subject)

    lectors = set()
    for l in data['lectors'].unique():
        for lector in l.split(','):
            lectors.add(lector)
    for lector in lectors:
        if get_lector_id(lector) is None:
            add_lector(lector)

    for i in range(0, len(data)):
        data_row = data.loc[i]
        write_single_record(*data_row[:-1], data_row[-1:].lectors.split(', '))
    log_msg = 'New timetable records added for group {0}'.format(data['group'].values[0])
    logger.info(log_msg)


def delete_day_records_for_group(day, group_id):
    sql = """
    DELETE FROM 
        lectors_subjects_composite
    WHERE c_id in
        (SELECT 
            class_id
            FROM 
                timetable 
            WHERE 
                (group_id = {0})
            AND
                (class_id in (SELECT c_id FROM classes WHERE day = \"{1}\")));""".format(group_id, day)
    c.execute(sql)
    sql = """
    DELETE FROM
        classes
    WHERE
        (c_id in (SELECT class_id FROM timetable WHERE group_id = {0}))
    AND
        (day = \"{1}\");""".format(group_id, day)
    c.execute(sql)
    conn.commit()
    log_msg = 'Records deleted by (day={0}, group_id={1})'.format(day, group_id)
    logger.info(log_msg)


def register_user(chat_id, username='NULL'):
    code = hash(str(chat_id))
    sql = 'INSERT INTO users (chat_id, username, verification_code) VALUES ({0}, \"{1}\", {2})'\
        .format(chat_id, username, code)
    c.execute(sql)
    conn.commit()
    log_msg = 'User {0} {1} was registered'.format(chat_id, username)
    logger.info(log_msg)


def delete_user(chat_id):
    sql = 'DELETE FROM users WHERE chat_id = {0}'.format(chat_id)
    c.execute(sql)
    conn.commit()
    log_msg = 'User {0} was deleted'.format(chat_id)
    logger.info(log_msg)


def subscribe(chat_id, group):
    group_id = get_group_id(group)
    if group_id is None:
        log_msg = 'User {0} is trying to subscribe to non-existing group ({1})'.format(chat_id, group)
        logger.warning(log_msg)
        return
    sql = "UPDATE users SET is_subscribed = 1, studing_group = {0}} WHERE chat_id = {1}".format(group_id, chat_id)
    c.execute(sql)
    conn.commit()
    log_msg = 'User {0} was subscribed'.format(chat_id)
    logger.info(log_msg)


def unsubscribe(chat_id):
    sql = "UPDATE users SET is_subscribed = 0 WHERE chat_id = {0}".format(chat_id)
    c.execute(sql)
    conn.commit()
    log_msg = 'User {0} was unsubscribed'.format(chat_id)
    logger.info(log_msg)


def is_user_subscribed(chat_id):
    sql = 'SELECT is_subscribed FROM users WHERE chat_id = {0}'.format(chat_id)
    c.execute(sql)
    return c.fetchone()[0]


def get_users():
    sql = 'SELECT * FROM users'
    users = []
    for row in c.execute(sql):
        users.append(row)
    return users

import dbController as dbc
import os


def read_groups(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            groups = []
            for row in file:
                groups.append(row.split())
            return groups


def add_groups(groups):
    for row in groups:
        group_name, facultet_id = row
        if dbc.get_group_id(group_name) is None:
            dbc.add_group(group_name, facultet_id)
    print('Job done!')


def add_data(filename):
    if os.path.exists(filename):
        data = dbc.read_csv(filename)
        dbc.write_timetable(data)
        print('Job done!')
    else:
        print('Path not exist!')

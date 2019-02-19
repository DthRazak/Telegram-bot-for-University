import dbController as dbc


def remove_by_day(day, group_name):
    group_id = dbc.get_group_id(group_name)
    if group_id is not None:
        dbc.delete_day_records_for_group(day, group_id)
        print("Job done!")
    else:
        print("Can't find group id!")

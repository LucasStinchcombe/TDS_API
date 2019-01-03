'''
Simple example bot I used for own scheduling.

I live >30 min away so I want to book 2 hours at a time.
On weekdays, the earliest I can make it is 7:00pm which is the second to last
block.
'''
import os
import sys
import tds_api

def _filter_late_weekdays(session):
    """
    Filters out availabilities that are weekdays before 7pm.
    """

    # if weekday
    if session['date'].weekday() < 5:

        for i in range(len(session['schedule']) - 2):
            if session['schedule'][i] == 'O':
                session['schedule'][i] = 'L'
    return session

def _filter_out_of_order(sessions):
    """
    Filters out availabilities that are before currently scheduled days.
    """
    for i in range(len(sessions)):

        session = sessions[i]

        # Find first 'J'
        if 'J' in session['schedule']:
            idx = session['schedule'].index('J')

            for j in range(idx):
                session['schedule'][j] = 'N'

            for k in range(i):
                sessions[k]['schedule'] = ['N'] * 13

    return sessions

def _apply_filters(sessions):
    """
    Apply all filters.
    """
    sessions = _filter_out_of_order(sessions)
    sessions = map(_filter_late_weekdays, sessions)
    return sessions

def main(args):
    """
    main routine gets cookies, gets availabilities.
    """
    username = os.environ['TDS_USERNAME']
    password = os.environ['TDS_PASSWORD']

    if len(args) > 1:
        username = args[0]
        password = args[1]

    cookies = tds_api.login(username, password)

    avails1 = tds_api.get_availability(cookies)
    avails1 = _apply_filters(avails1)



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

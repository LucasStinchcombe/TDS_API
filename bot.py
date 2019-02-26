'''
Simple example bot I used for my own scheduling.
'''
import os
import sys
import api
import time
import signal
import logging

from datetime import datetime, timedelta

SLEEP_SECONDS = 60
STOP_EVENT = False

def sigint_handler(sig, frame):
    global STOP_EVENT
    STOP_EVENT = True

signal.signal(signal.SIGINT, sigint_handler)


def _filter_work_hours(x):
    """
    Filter out work hours.
    """
    if (x['datetime'].weekday() < 5
            and x['datetime'].hour < 19):
        return False
    else:
        return True

def _filter_non_cancellable(x):
    """
    Filter out sessions that are less than or equal to 24 hours away.
    """
    return x['datetime'] > datetime.now() + timedelta(hours=24)


def main(args):
    """
    main routine gets cookies, gets availabilities.
    """
    username = os.environ['TDS_USERNAME']
    password = os.environ['TDS_PASSWORD']

    if len(args) > 1:
        username = args[0]
        password = args[1]

    while not STOP_EVENT:
        try:
            cookies = api.login(username, password)

            schedule = api.schedule.get(cookies)
            schedule = list(filter(_filter_work_hours, schedule))

            avails = []
            for session in reversed(schedule):
                if session['status'] == 'O':
                    avails.append(session)
                elif session['status'] == 'J':
                    break

            for session in reversed(avails):
                logging.INFO('registering session: ', session)
                api.schedule.register(session)

        except:
            # IGNORE EVERYTHING, KEEP GOING
            pass

        finally:
            for i in range(SLEEP_SECONDS):
                if STOP_EVENT:
                    break

                time.sleep(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

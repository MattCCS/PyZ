
import os

import signal
from functools import wraps


class TimesUpException(Exception):
    pass


def timeout(seconds=1.0, error_message="Time's up!"):

    def decorator(func):

        def _handle_timeout(signum, frame):
            raise TimesUpException(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.setitimer(signal.ITIMER_REAL,seconds) #used timer instead of alarm
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)

            return result

        return wraps(func)(wrapper)

    return decorator

# the 'stty size' command randomly takes FOREVER to return.
# so, we just ask again.
# THIS IS NOT WINDOWS COMPATIBLE!!!
@timeout(seconds=0.01)
def _true_terminal_size():
    (rows, columns) = os.popen('stty size', 'r').read().split()
    return (int(columns), int(rows))

def true_terminal_size():
    for i in range(10):
        try:
            return _true_terminal_size()
        except TimesUpException:
            continue

    raise RuntimeError("Terminal not responding!")

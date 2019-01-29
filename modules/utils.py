# Utils.py
import datetime
from datetime import timedelta
from dateutil import parser


def shrink(t, start, end):
    "Return `t` clamped to the range [`start`, `end`]."
    return max(start, min(end, t))

def day_part(t):
    "Return timedelta between midnight and `t`."
    return t - t.replace(hour = 0, minute = 0, second = 0)

def office_time_between(a, b, start = timedelta(hours = 8, minutes = 30),
                        stop = timedelta(hours = 17, minutes = 30)):
    """
    Return the total office time between `a` and `b` as a timedelta
    object. Office time consists of weekdays from `start` to `stop`
    (default: 08:30 to 17:30).
    """
    zero = timedelta(0)
    assert(zero <= start <= stop <= timedelta(1))
    office_day = stop - start
    days = (b - a).days + 1
    weeks = days // 7
    extra = (max(0, 5 - a.weekday()) + min(5, 1 + b.weekday())) % 5
    weekdays = weeks * 5 + extra
    total = office_day * weekdays
    if a.weekday() < 5:
        total -= shrink(day_part(a) - start, zero, office_day)
    if b.weekday() < 5:
        total -= shrink(stop - day_part(b), zero, office_day)
    return total

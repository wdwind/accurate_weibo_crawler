import calendar
from datetime import datetime, timedelta
from dateutil import parser

def get_current_unix_time():
    """
    Get current unix time.

    """
    unix_now = calendar.timegm(datetime.utcnow().utctimetuple())
    return unix_now

def parse_time_string(t, tz=None):
    """
    Parse time string t.
    tz is the timezone string, like '+0800'.

    """
    if tz is not None:
        t += ' ' + tz
    t = parser.parse(t)
    return calendar.timegm(t.utctimetuple())

    
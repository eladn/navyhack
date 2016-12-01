import MySQLdb
from secrets import *

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def db_connect():
    try:
        return MySQLdb.connect(cnx['HOST'], cnx['USER'], cnx['PASSWORD'], cnx['db'], charset='utf8', use_unicode=True)
    except Exception:
        return None


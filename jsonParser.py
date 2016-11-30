import sys
import MySQLdb
from secrets import *
import json
from urllib3 import PoolManager
import time
#from collections import namedtuple
from datetime import datetime
from pytz import timezone

from utils import safe_cast

MAX_NR_ROWS_PER_UPDATE = 10000

MMSI = 0
LAT = 0
LONG = 1
SPEED = 2
COURSE = 3
REPORTED_UPDATE_TIME = 6
GRABBER_UPDATE_TIME = 7

il_tz = timezone('Israel')

#f = open("parser.txt","w")
decoder = lambda t:t.decode()

httpPool = PoolManager()
sleep_minutes = {'shipfinder': 1}

def grab_data_from_shipfinder(ships):
    lastUpdate = ships['last_update']
    url = "http://shipfinder.co/endpoints/shipDeltaUpdate.php"
    response = httpPool.request('GET', url)
    if response.status is not 200:
        return None

    try:
        j = json.loads(response.data.decode('utf-8'))
        # TODO: maybe try to change the sleep time here
    except Exception:
        return None

    ships_data = j['ships']
    if ships_data is None or len(ships_data) < 1:
        return None

    # for statics
    nr_items = len(ships_data)
    nr_new_items = 0
    nr_updated_items = 0

    now = datetime.now(il_tz)
    for mmsi, vals in ships_data.items():
        mmsi = safe_cast(mmsi, int)
        if mmsi is None:
            # TODO: log it somehow
            continue
        if mmsi not in lastUpdate:
            nr_new_items += 1
            lastUpdate[mmsi] = dict()
        elif lastUpdate[mmsi][REPORTED_UPDATE_TIME] is safe_cast(vals[REPORTED_UPDATE_TIME], int):
            lastUpdate[mmsi][GRABBER_UPDATE_TIME] = now
            continue
        else:
            nr_updated_items += 1

        ship = lastUpdate[mmsi]
        ship[LAT] = safe_cast(vals[LAT], float)
        ship[LONG] = safe_cast(vals[LONG], float)
        ship[SPEED] = safe_cast(vals[SPEED], float)
        ship[COURSE] = safe_cast(vals[COURSE], float)
        ship[REPORTED_UPDATE_TIME] = safe_cast(vals[REPORTED_UPDATE_TIME], int)
        ship[GRABBER_UPDATE_TIME] = now
        ships['modified'].add(mmsi)  # mark it as changed so a db update will occur

    return {'nr_items': nr_items, 'nr_new_items': nr_new_items, 'nr_updated_items': nr_updated_items}

def init(): #TODO
    # select mmsi, update from table parse it into lastUpdate[mmsi] = update
    pass


def db_connect():
    try:
        return MySQLdb.connect(cnx['HOST'], cnx['USER'], cnx['PASSWORD'], cnx['db'], charset='utf8', use_unicode=True)
    except Exception:
        return None


def convert_ship_data_to_sql_insert_values(mmsi, ship_data):
    #values = list(map(decoder, ship_data))  # already decoded
    values = ship_data
    sValues = "({}, '{}', '{}', {}, {}, {}, {})".format(
                mmsi, datetime.fromtimestamp(values[REPORTED_UPDATE_TIME]).strftime('%Y-%m-%d %H:%M:%S'),
                values[GRABBER_UPDATE_TIME].strftime('%Y-%m-%d %H:%M:%S'), values[LAT],
                values[LONG], values[SPEED], values[COURSE])
    return sValues


def update_db(ships, db):
    if db is None:
        return 0

    if len(ships['modified']) < 1:
        return 0  # nothing to update

    tot_affected_rows = 0
    while len(ships['modified']) > 0:
        rows = 0
        st = "INSERT INTO ship_tracks(mmsi,reported_time,last_grab_time,lat,lon,speed,course) VALUES "
        values = ''
        updated_ships = set()  # we cannot remove them from `modified` while iterate.
        for ship_mmsi in ships['modified']:
            rows += 1
            if rows > MAX_NR_ROWS_PER_UPDATE:
                break
            ship_data = ships['last_update'][ship_mmsi]
            values += convert_ship_data_to_sql_insert_values(ship_mmsi, ship_data) + ","
            updated_ships.add(ship_mmsi)
        assert len(values) > 1
        st += values[:-1] + " on duplicate key UPDATE last_grab_time = VALUES(last_grab_time)"  # remove last comma

        ships['modified'].difference_update(updated_ships)  # remove updated ships from modified

        try:
            cursor = db.cursor()
            tot_affected_rows += cursor.execute(st + ";")
            db.commit()
        except MySQLdb.IntegrityError:
            print("failed to insert values.", file=sys.stderr)
        finally:
            cursor.close()
    return tot_affected_rows


def iterative_interrupted_data_grabber(ships, db, sleep_time=5):
    iteration = 0
    while True:
        iteration += 1
        print("Running loop number %s                                                       " % iteration, end="\r")

        stats = grab_data_from_shipfinder(ships)
        if stats is not None:
            print("Running loop number {}  [ shipfinder: tot:{} updated:{} new:{} ]".format(
                iteration, stats['nr_items'], stats['nr_updated_items'], stats['nr_new_items']), end="\r")

        affected_rows = update_db(ships, db)
        print("Running loop number {}  [ db affected rows: {} ]                             ".format(
            iteration, affected_rows), end="\r")
        time.sleep(sleep_time)


def create_ships_ds():
    return {
        'last_update': dict(),
        'modified': set()
    }


DEFAULT_SLEEP_SEC = 60
def args_parser():
    import argparse
    parser = argparse.ArgumentParser(description='Grabber for naval data.')
    parser.add_argument('--nodb', help='do not update db.', action="store_true")
    parser.add_argument('--sleep', default=DEFAULT_SLEEP_SEC, type=int, choices=range(5, 60*20),
                        metavar="[{}-{}]".format(5, 60*20), help='sleep time between requests.')
    return parser


if __name__ == "__main__":
    parser = args_parser()
    args = parser.parse_args()

    db = None
    if args.nodb:
        print('no db updated option selected.')
    else:
        db = db_connect()
        if db is None:
            print('cant connect to elad`s db, blame him!#!', file=sys.stderr)
            exit()
        print('db connection succeeded')

    ships = create_ships_ds()
    iterative_interrupted_data_grabber(ships, db, args.sleep)




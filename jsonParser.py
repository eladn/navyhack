import MySQLdb
from secrets import *
import json
from urllib3 import PoolManager
import time
#from collections import namedtuple
from datetime import datetime
from utils import safe_cast

MAX_NR_ROWS_PER_UPDATE = 10000

MMSI = 0
LAT = 0
LONG = 1
SPEED = 2
COURSE = 3
REPORTED_UPDATE_TIME = 6
GRABBER_UPDATE_TIME = 7


#f = open("parser.txt","w")
decoder = lambda t:t.decode()

httpPool = PoolManager()

def grab_data_from_shipfinder(ships):
    lastUpdate = ships['last_update']
    url = "http://shipfinder.co/endpoints/shipDeltaUpdate.php"
    response = httpPool.request('GET', url)
    if response.status is not 200:
        return None

    j = json.loads(response.data.decode('utf-8'))
    ships_data = j['ships']
    if ships_data is None or len(ships_data) < 1: return None

    # for statics
    nr_items = len(ships_data)
    nr_new_items = 0
    nr_updated_items = 0

    now = datetime.now()
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
    if len(ships['modified']) < 1:
        return None  # nothing to update

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
            affected_count = cursor.execute(st + ";")
            db.commit()
        except MySQLdb.IntegrityError:
            print("failed to insert values.")
        finally:
            cursor.close()


def iterative_interrupted_data_grabber(ships, db, sleep_time=5):
    iteration = 0
    while True:
        iteration += 1
        print("Running loop number %s                                                             " % iteration, end="\r")
        stats = grab_data_from_shipfinder(ships)
        if stats is not None:
            print("Running loop number {}  [shipfinder: tot:{} updated:{} new:{}]".format(
                iteration, stats['nr_items'], stats['nr_updated_items'], stats['nr_new_items']), end="\r")
        update_db(ships, db)
        time.sleep(sleep_time)


def create_ships_ds():
    return {
        'last_update': dict(),
        'modified': set()
    }

if __name__ == "__main__":
    db = db_connect()
    if db is None:
        print('cant connect to elad`s db, blame him!#!')
        exit()
    print('db connection succeeded')

    #print('2016 - 11 - 30 14:39:55.192458'.strftime('%Y-%m-%d %H:%M:%S'))
    #st = "INSERT INTO ship_tracks(mmsi,reported_time,lat,long,speed,course) VALUES(376832000, '2016 - 11 - 30 14:39:55.192458', 10.3584, -61.5, 0, 0);"
    #cursor = db.cursor()
    #cursor.execute(st )
    #exit()

    ships = create_ships_ds()
    iterative_interrupted_data_grabber(ships, db)




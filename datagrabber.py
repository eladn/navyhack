import sys
import MySQLdb
import json
from urllib3 import PoolManager
import time
from datetime import datetime
from pytz import timezone
from utils import db_connect
from utils import safe_cast
from math import ceil, floor

MAX_NR_ROWS_PER_UPDATE = 10000
MAX_NR_SHIPS_INFO_GRAB = 30
NR_SUCCEED_REQUEST_TO_INC_ZOOM = 5

MMSI = 0
LAT = 0
LONG = 1
SPEED = 2
COURSE = 3
REPORTED_UPDATE_TIME = 6
GRABBER_UPDATE_TIME = 7
DATA_SOURCE = 8
NR_SHIP_FIELDS = 9

SHIPFINDER_DATA_SOURCE = 0
MYSHIPTRACKING_DATA_SOURCE = 1

il_tz = timezone('Israel')

decoder = lambda t:t.decode()

httpPool = PoolManager()
sleep_minutes = {'shipfinder': 1}

def grab_data_from_shipfinder(ships):
    lastUpdate = ships['last_update']
    shipSet = ships['avail']
    # print(shipSet)
    url = "http://shipfinder.co/endpoints/shipDeltaUpdate.php"
    response = httpPool.request('GET', url)
    if response.status is not 200:
        print('shipfinder grab status no 200 err. url: %s'%url, file=sys.stderr)
        return None

    try:
        str = response.data.decode('utf-8')
        str = str[str.index('{'):]
        j = json.loads(str)
        # TODO: maybe try to change the sleep time here
    except Exception:
        print('shipfinder grab json parse err. url: %s'%url, file=sys.stderr)
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
            print('shipfinder None mmsi . url: %s'%url, file=sys.stderr)
            continue
        if mmsi not in lastUpdate:
            nr_new_items += 1
            lastUpdate[mmsi] = dict()
        elif lastUpdate[mmsi][REPORTED_UPDATE_TIME] == safe_cast(vals[REPORTED_UPDATE_TIME], int):
            lastUpdate[mmsi][GRABBER_UPDATE_TIME] = now
            continue
        else:
            nr_updated_items += 1
        if mmsi not in shipSet:
            ships['avail'].add(mmsi)
            ships['infoSearch'].add(mmsi)

        ship = lastUpdate[mmsi]
        ship[LAT] = safe_cast(vals[LAT], float)
        ship[LONG] = safe_cast(vals[LONG], float)
        ship[SPEED] = safe_cast(vals[SPEED], float)
        ship[COURSE] = safe_cast(vals[COURSE], float)
        ship[REPORTED_UPDATE_TIME] = safe_cast(vals[REPORTED_UPDATE_TIME], int)
        ship[GRABBER_UPDATE_TIME] = now
        ship[DATA_SOURCE] = SHIPFINDER_DATA_SOURCE
        ships['modified'].add(mmsi)  # mark it as changed so a db update will occur
    return {'nr_items': nr_items, 'nr_new_items': nr_new_items, 'nr_updated_items': nr_updated_items}


myshiptracking_data = {
    'geo_areas': [
        {
            'min_lat': 28.84750,
            'min_lon': -12.97300,
            'max_lat': 46.72501,
            'max_lon': 38.27735,
            'zoom': 7,
            'lat_delta': 2,
            'lon_delta': 2,
            'max_nr_requests_per_cycle': 40,
            'last_zoom_per_cell': {}
        }
    ],
    'max_tot_nr_requests_per_cycle': 50,
    'min_zoom': 5
}


def myshiptracking_init():
    for area in myshiptracking_data['geo_areas']:
        area['nr_rows'] = ceil((ceil(area['max_lat']) - floor(area['min_lat'])) / area['lat_delta'])
        area['nr_cols'] = ceil((ceil(area['max_lon']) - floor(area['min_lon'])) / area['lon_delta'])





def grab_data_from_myshiptracking(ships):
    max_tot_nr_requests_per_cycle = myshiptracking_data['max_tot_nr_requests_per_cycle']
    tot_nr_requests = 0
    ret_stats = {'nr_items': 0, 'nr_new_items': 0, 'nr_updated_items': 0}

    for area in myshiptracking_data['geo_areas']:
        start_lat = floor(area['min_lat'])
        start_lon = floor(area['min_lon'])
        lat_delta = area['lat_delta']
        lon_delta = area['lon_delta']
        nr_rows = area['nr_rows']
        nr_cols = area['nr_cols']
        max_nr_requests_per_cycle = area['max_nr_requests_per_cycle']

        nr_requests = 0

        start_col, start_row = 1, 1
        if 'last_unfinished_cover' in area:
            start_col, start_row = area['last_unfinished_cover']['next_col'], area['last_unfinished_cover']['next_row']

        flag_end_area = False
        for row in range(start_row, nr_rows-1):
            for col in range(start_col, nr_cols-1):
                area['last_unfinished_cover'] = {'next_row': row, 'next_col': col}
                if tot_nr_requests >= max_tot_nr_requests_per_cycle:
                    return ret_stats
                if nr_requests >= max_nr_requests_per_cycle:
                    flag_end_area = True
                    break

                custom_zoom = area['zoom']
                if (row, col) in area['last_zoom_per_cell']:
                    custom_zoom = area['last_zoom_per_cell'][(row, col)][0]

                stat = grab_data_from_myshiptracking_cell(ships,
                                                   start_lat+row*lat_delta, start_lat+(row+1)*lat_delta,
                                                   start_lon+col*lon_delta, start_lon+(col+1)*lon_delta, custom_zoom)

                # we'll try next time with a lower zoom
                if stat is None:
                    area['last_zoom_per_cell'][(row, col)] = (max(myshiptracking_data['min_zoom'], custom_zoom-1), 0)
                elif (row, col) in area['last_zoom_per_cell']:
                    times_succeeded_with_this_zoom = area['last_zoom_per_cell'][(row, col)][1]
                    area['last_zoom_per_cell'][(row, col)] = (custom_zoom, times_succeeded_with_this_zoom+1)

                    # increment zoom for next time if we succeeded with current zoom for `NR_SUCCEED_REQUEST_TO_INC_ZOOM` times
                    if times_succeeded_with_this_zoom+1 >= NR_SUCCEED_REQUEST_TO_INC_ZOOM:
                        area['last_zoom_per_cell'][(row, col)] = (max(1, custom_zoom + 1), 0)

                if stat is not None:
                    ret_stats['nr_items'] += stat['nr_items']
                    ret_stats['nr_new_items'] += stat['nr_new_items']
                    ret_stats['nr_updated_items'] += stat['nr_updated_items']

                nr_requests += 1
                tot_nr_requests += 1
            if flag_end_area:
                break

        if not flag_end_area and 'last_unfinished_cover' in area:
            del area['last_unfinished_cover']

    return ret_stats


def grab_data_from_myshiptracking_cell(ships, min_lat, max_lat, min_lon, max_lon, zoom):
    lastUpdate = ships['last_update']
    shipSet = ships['avail']

    url = 'http://www.myshiptracking.com/requests/vesselsonmap.php?type=json&minlat={}&maxlat={}&minlon={}&maxlon={}&zoom={}&mmsi=null'.format(
        min_lat, max_lat, min_lon, max_lon, zoom
    )
    response = httpPool.request('GET', url)
    if response.status is not 200:
        print('myshiptracking grab 200 err. url: %s'%url, file=sys.stderr)
        return None

    try:
        j = json.loads(response.data.decode('utf-8'))
        # TODO: maybe try to change the sleep time here
    except Exception:
        print('myshiptracking grab json parse err. url: %s'%url, file=sys.stderr)
        return None

    if type(j) != list or len(j) < 1:
        print('myshiptracking grab json parse err: no list. url: %s'%url, file=sys.stderr)
        return None

    if type(j[0]) != dict or 'DATA' not in j[0]:
        print('myshiptracking grab json parse err: no `DATA` key in list. url: %s'%url, file=sys.stderr)
        return None

    ships_data = j[0]['DATA']
    if ships_data is None or type(ships_data) != list:
        print('myshiptracking grab json err: no list in `DATA`. url: %s'%url, file=sys.stderr)
        return None

    if len(ships_data) < 1:
        #print('myshiptracking grab err: empty data', file=sys.stderr)
        return None

    # for statics
    nr_items = len(ships_data)
    nr_new_items = 0
    nr_updated_items = 0

    fields = {
        'COG': COURSE,
        'SOG': SPEED,
        'R': REPORTED_UPDATE_TIME,
        'LAT': LAT,
        'LNG': LONG
    }

    now = datetime.now(il_tz)
    for item in ships_data:
        if type(item) != dict:
            print('myshiptracking grab err: ship item is not a dict', file=sys.stderr)
            continue

        if 'MMSI' not in item:
            print('myshiptracking grab err: no mmsi for record', file=sys.stderr)
            continue
        mmsi = safe_cast(item['MMSI'], int)
        if mmsi is None:
            print('myshiptracking grab err: invalid mmsi (not int)', file=sys.stderr)
            continue

        if len(set(fields) - set(item)) > 0:
            print('myshiptracking grab err: no all req fields', file=sys.stderr)
            continue

        vals = [0]*NR_SHIP_FIELDS
        for field_name, to_idx in fields.items():
            vals[to_idx] = item[field_name]

        if mmsi not in lastUpdate:
            nr_new_items += 1
            lastUpdate[mmsi] = dict()
        elif lastUpdate[mmsi][REPORTED_UPDATE_TIME] == safe_cast(vals[REPORTED_UPDATE_TIME], int):
            lastUpdate[mmsi][GRABBER_UPDATE_TIME] = now
            continue
        else:
            nr_updated_items += 1
        if mmsi not in shipSet:
            ships['avail'].add(mmsi)
            ships['infoSearch'].add(mmsi)

        ship = lastUpdate[mmsi]
        ship[LAT] = safe_cast(vals[LAT], float)
        ship[LONG] = safe_cast(vals[LONG], float)
        ship[SPEED] = safe_cast(vals[SPEED], float)
        ship[COURSE] = safe_cast(vals[COURSE], float)
        ship[REPORTED_UPDATE_TIME] = safe_cast(vals[REPORTED_UPDATE_TIME], int)
        ship[GRABBER_UPDATE_TIME] = now
        ship[DATA_SOURCE] = MYSHIPTRACKING_DATA_SOURCE
        ships['modified'].add(mmsi)  # mark it as changed so a db update will occur
    return {'nr_items': nr_items, 'nr_new_items': nr_new_items, 'nr_updated_items': nr_updated_items}



def updateInfoSearch(ships):
    llen = len(ships['infoSearch'])
    newInfo = []
    if(llen > MAX_NR_SHIPS_INFO_GRAB):
        llen = MAX_NR_SHIPS_INFO_GRAB
    infoToSearch = list(ships['infoSearch'])[:llen]

    for mmsi in infoToSearch:
        grab_data_for_specific_ship(ships, mmsi)
        time.sleep(0.2)
    return newInfo, llen



def grab_data_for_specific_ship(ships, mmsi):
    TYPE = 2
    FLAG = 1
    NAME = 0
    DESTINATION = 3
    NAV_STATUS = 4
    INFO_FOUNT = 5

    url = "http://www.myshiptracking.com/requests/vesseldetails.php?type=json&mmsi="+str(mmsi)
    # print(url)

    ships['infoSearch'].remove(mmsi)
    ships['infoModified'].add(mmsi)
    results = [""] * 6
    results[INFO_FOUNT] = 0
    ships['information'][mmsi] = results

    response = httpPool.request('GET', url)
    if response.status is not 200:
        print('myshiptracking ship_info: status is not 200. url: %s' % url, file=sys.stderr)
        return None
    try:
        j = json.loads(response.data.decode('utf-8'))
        # TODO: maybe try to change the sleep time here
    except Exception:
        print('myshiptracking ship_info: json parse error. url: %s' % url, file=sys.stderr)
        return None

    if "V" not in j:
        print('myshiptracking ship_info: json parse error. no `V`. url: %s' % url, file=sys.stderr)
        return None

    j = j["V"]
    try:
        results[TYPE] = safe_cast(j["VESSEL_TYPE"], str)
        results[FLAG] = safe_cast(j["FLAG"], str)
        results[NAME] = safe_cast(j["NAME"], str)
        results[DESTINATION] = safe_cast(j["DESTINATION"], str)
        results[NAV_STATUS] = safe_cast(j["NAV_STATUS"], str)
        results[INFO_FOUNT] = 1
    except Exception:
        return None



def convert_ship_data_to_sql_insert_values(mmsi, ship_data):
    values = ship_data
    sValues = "({}, '{}', '{}', {}, {}, {}, {}, {})".format(
                mmsi, datetime.fromtimestamp(values[REPORTED_UPDATE_TIME]).strftime('%Y-%m-%d %H:%M:%S'),
                values[GRABBER_UPDATE_TIME].strftime('%Y-%m-%d %H:%M:%S'), values[LAT],
                values[LONG], values[SPEED], values[COURSE], values[DATA_SOURCE])
    return sValues


def update_db(ships, db):
    if db is None:
        return 0

    if len(ships['modified']) < 1:
        return 0  # nothing to update

    tot_affected_rows = 0
    while len(ships['modified']) > 0:
        rows = 0
        st = "INSERT INTO ship_tracks(mmsi,reported_time,last_grab_time,lat,lon,speed,course,source) VALUES "
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


def update_info_to_db(ships, db):
    if db is None:
        return 0

    if len(ships['infoModified']) < 1:
        return 0  # nothing to update

    tot_affected_rows = 0
    infoList = []
    for ship_mmsi in ships['infoModified']:
        infoList.append(tuple([ship_mmsi] + ships['information'][ship_mmsi]))
    ships['infoModified'] = set()
    cursor = db.cursor()

    try:
        tot_affected_rows = cursor.executemany(
            "INSERT INTO ship_info(mmsi, shipname, flag, vessel_type, destination, nav_status, info_found) "
                           "VALUES (%s,%s,%s,%s,%s,%s,%s)",infoList)
        db.commit()
    except Exception as e:
        print(e, file=sys.stderr)
    finally:
        cursor.close()
    return tot_affected_rows


def iterative_interrupted_data_grabber(ships, db, sleep_time=5, noinfo=False, noloc=False):
    iteration = 0
    while True:
        iteration += 1
        print("Running loop number %s                                                       " % iteration, end="\r")

        stats = None
        if not noloc:
            stats = grab_data_from_shipfinder(ships)
        if stats is not None:
            print("Running loop number {}  [ shipfinder: tot:{} updated:{} new:{} ]              ".format(
                iteration, stats['nr_items'], stats['nr_updated_items'], stats['nr_new_items']), end="\r")

        stats = None
        if not noloc:
            stats = grab_data_from_myshiptracking(ships)
        if stats is not None:
            print("Running loop number {}  [ myshiptracking: tot:{} updated:{} new:{} ]            ".format(
                iteration, stats['nr_items'], stats['nr_updated_items'], stats['nr_new_items']), end="\r")

        infoStats = None
        if not noinfo:
            infoStats = updateInfoSearch(ships)
        if infoStats is not None:
            print('Running loop number {}  [ myshiptracking ship info grabbed: {} ]               '.format(iteration, infoStats[1]))
        #('infoState:{}'.format(infoStats[1]) if infoStats[1] is not 0 else '')

        if db is not None:
            if not noloc:
                affected_rows = update_db(ships, db)
                print("Running loop number {}  [ db affected rows: {} ]                             ".format(
                    iteration, affected_rows), end="\r")
            if not noinfo:
                affected_rows = update_info_to_db(ships, db)
                print("Running loop number {}  [ db info affected rows: {} ]                             ".format(
                    iteration, affected_rows), end="\r")

        time.sleep(sleep_time)


def create_ships_ds(db):
    d = {
        'last_update': dict(),
        'information': dict(),
        'modified': set(),
        'infoModified': set(),
        'avail': set(),
        'infoSearch': set()
    }
    if db is None:
        return d
    queryHistoryShips = "SELECT DISTINCT mmsi from ship_tracks"
    queryInfoShips = "SELECT DISTINCT mmsi from ship_info"

    cursor = db.cursor()
    cursor.execute(queryHistoryShips)
    ### parse cursor
    changer = lambda x:x[0]
    d['avail'] = set(changer(row) for row in cursor.fetchall())
    cursor.execute(queryInfoShips)
    d['infoSearch'] = d['avail'].difference(set(changer(row) for row in cursor.fetchall()))

    return d



DEFAULT_SLEEP_SEC = 60
def args_parser():
    import argparse
    parser = argparse.ArgumentParser(description='Grabber for naval data.')
    parser.add_argument('--nodb', help='do not update db.', action="store_true")
    parser.add_argument('--noinfo', help='do not grab ships info.', action="store_true")
    parser.add_argument('--noloc', help='do not grab ships new reported locations.', action="store_true")
    parser.add_argument('--sleep', default=DEFAULT_SLEEP_SEC, type=int, choices=range(5, 60*20),
                        metavar="[{}-{}]".format(5, 60*20), help='sleep time between requests.')
    return parser


def init():
    myshiptracking_init()

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

    init()
    ships = create_ships_ds(db)
    iterative_interrupted_data_grabber(ships, db, args.sleep, args.noinfo, args.noloc)




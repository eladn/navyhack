import pickle
import MySQLdb
from secrets import *
import argparse
import json
import itertools
def db_connect():
    try:
        return MySQLdb.connect(cnx['HOST'], cnx['USER'], cnx['PASSWORD'], cnx['db'], charset='utf8', use_unicode=True)
    except Exception as e:
        print("Cannot connect")
        print(e)
        return None
DEFAULT_SLEEP_SEC = 6
def args_parser():

    parser = argparse.ArgumentParser(description='Grabber for naval data.')
    parser.add_argument('--nodb', help='do not update db.', action="store_true")
    parser.add_argument('--sleep', default=DEFAULT_SLEEP_SEC, type=int, choices=range(5, 60*20),
                        metavar="[{}-{}]".format(5, 60*20), help='sleep time between requests.')
    return parser



def create_ships_ds():
    return {

    }


def makeItWorks(db, ships):
    # f = open("parser.txt","wb")
    cursor = db.cursor()
    st = "SELECT vessel_type, ship_type FROM vessel_type_to_ship_type;"
    cursor.execute(st)
    vessel_type_to_ship_type = {}
    for row in cursor.fetchall():
        assert len(row) >= 2
        vessel_type_to_ship_type[row[0]] = row[1]
    cursor.close()
    print('nr of vessel_types: %s' % len(vessel_type_to_ship_type))
    with open("vessel_type_to_ship_type.pkl","wb") as pf:
        pickle.dump(vessel_type_to_ship_type, pf)

    cursor = db.cursor()
    st = "SELECT DISTINCT mmsi from ship_tracks;"
    cursor.execute(st)
    d = {}
    shipList = []
    for row in cursor.fetchall():
        shipList.append(row[0])

    print('nr of distinct mmsi from ship_tracks: %s' % len(shipList))
    infos = {}
    tempquery = "SELECT mmsi, shipname, flag, vessel_type, destination, nav_status, info_found from ship_info;"
    cursor.execute(tempquery)
    i = 0
    for elem in cursor.fetchall():
        infos[elem[0]] = list(elem)
    for mmsi in shipList:
        if(i % 3000 is 0):
            print("we are in entity number %s" %i)
        i+=1
        d[mmsi] = [[],[],[]]
        tempquery = "SELECT mmsi, lat, lon, course, speed, reported_time from ship_tracks where mmsi = %s;" %mmsi
        cursor.execute(tempquery)
        for row in cursor.fetchall():
            d[mmsi][0].append(row)
        if(mmsi not in infos):
            continue
        d[mmsi][1] = infos[mmsi]
    cursor.close()
    j = list(d.items())
    lower = 0
    print(len(j))
    partial = int((1/6) * len(j))
    with open("bestPickleEver1.txt","wb") as f:
        pickle.dump(j[0:5000],f)
    with open("bestPickleEver%s.txt" % 2, "wb") as f:
        pickle.dump(j[5000:10000], f)
    with open("bestPickleEver%s.txt" % 3, "wb") as f:
        pickle.dump(j[10000:15000], f)
    with open("bestPickleEver%s.txt"%4,"wb") as f:
        pickle.dump(j[15000:20000],f)
    with open("bestPickleEver%s.txt"%5,"wb") as f:
        pickle.dump(j[20000:25000],f)
    with open("bestPickleEver%s.txt"%6,"wb") as f:
        pickle.dump(j[25000:30000],f)
    with open("bestPickleEver%s.txt" % 7, "wb") as f:
        pickle.dump(j[30000:35000], f)
    with open("bestPickleEver%s.txt" % 8, "wb") as f:
        pickle.dump(j[35000:40000], f)
    with open("bestPickleEver%s.txt" % 9, "wb") as f:
        pickle.dump(j[40000:45000], f)
    with open("bestPickleEver%s.txt" % 10, "wb") as f:
        pickle.dump(j[45000:50000], f)
    with open("bestPickleEver%s.txt" % 11, "wb") as f:
        pickle.dump(j[50000:-1], f)



parser = args_parser()
args = parser.parse_args()
db = None
if args.nodb:
    print('no db updated option selected.')
else:
    db = db_connect()
makeItWorks(db, create_ships_ds())



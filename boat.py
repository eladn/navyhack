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
    f = open("parser.txt","wb")
    cursor = db.cursor()
    st = "SELECT DISTINCT mmsi from ship_tracks;"
    cursor.execute(st)
    d = {}
    shipList = []
    for row in cursor.fetchall():
        shipList.append(row[0])
    lengthOfList = len(shipList)
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
    j = iter(d.items())
    for i in range(10):
        with open("bestPickleEver%s.txt"%i,"wb") as f:
            pickle.dump(dict(itertools.islice(j,int(((i)/10)*len(d)),int(((i+1)/10)*len(d)))),f,2)



parser = args_parser()
args = parser.parse_args()
db = None
if args.nodb:
    print('no db updated option selected.')
else:
    db = db_connect()
makeItWorks(db, create_ships_ds())



import MySQLdb
from secrets import *
import json
from urllib import urlopen
import time


MMSI = 0
LAT = 0
LONG = 1
SPEED = 2
COURSE = 3
UPDATE_TIME = 6


f = open("parser.txt","w")
lastUpdate = {}
decoder = lambda t:t.decode()


def addIntoDb(mmsi, values):
    values = list(map(decoder, values))
    sValues = "(%s, %s, %s, %s, %s, %s)" \
            %(mmsi, values[LAT], values[LONG], values[SPEED], values[COURSE], values[UPDATE_TIME])
    return sValues
def query(db):
    url = urlopen("http://shipfinder.co/endpoints/shipDeltaUpdate.php")
    if(url.getcode() is 200):
        j = json.loads(url.read())
        ships = j['ships']
        st = "ADD INTO ShipTracks(mmsi,lat,long,speed,course,time) VALUES"
        for mmsi, vals in ships.items():
            if(mmsi in lastUpdate) and (lastUpdate[mmsi] is vals[UPDATE_TIME].decode()):
                continue
            lastUpdate[mmsi.decode()] = vals[UPDATE_TIME].decode()
            st += addIntoDb(mmsi.decode(), vals)+","
        st = st[:-1]
        print st[0:100]
        print st[-100:]
        # db.execute(st+";")
        # db.commit()
def init(): #TODO
    # select mmsi, update from table parse it into lastUpdate[mmsi] = update
    pass


if __name__ == "__main__":
    try:
        db = MySQLdb.connect(cnx['HOST'], cnx['USER'], cnx['PASSWORD'], cnx['db'], charset='utf8', use_unicode=True)
        print 'success'
        i = 0
        init()
        while True:
            print("running loop number %s" % i)
            query(db)
            time.sleep(5)
            i += 1
    except Exception:
        print 'cant connect to elad`s db, blame him!#!'
        exit()



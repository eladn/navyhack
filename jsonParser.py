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


def addIntoDb(mmsi, values,f):
    values = list(map(decoder, values))
    query = "ADD INTO ShipTracks(mmsi,lat,long,speed,course,time) VALUES(%s, %s, %s, %s, %s, %s);" \
            %(mmsi, values[LAT], values[LONG], values[SPEED], values[COURSE], values[UPDATE_TIME])

    f.write(query)
    f.write("\n")
def query():
    url = urlopen("http://shipfinder.co/endpoints/shipDeltaUpdate.php")

    if(url.getcode() is 200):
        j = json.loads(url.read())
        ships = j['ships']
        with open("parser.txt", "w") as f:
            for mmsi, vals in ships.items():
                if(mmsi in lastUpdate) and (lastUpdate[mmsi] is vals[UPDATE_TIME].decode()):
                    print "Ship number %s didnt change " %mmsi
                    continue
                lastUpdate[mmsi.decode()] = vals[UPDATE_TIME].decode()
                addIntoDb(mmsi.decode(), vals, f    )


if __name__ == "__main__":
    MySQLdb.connect(cnx['HOST'], cnx['USER'], cnx['PASSWORD'], cnx['db'], charset='utf8', use_unicode=True)
    print 'success'



    i = 0
    while True:
        print("running loop number %s" %i)
        query()
        time.sleep(5)
        i+=1

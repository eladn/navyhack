import pickle
TRACKING = 0
INFO = 1
EVAL = 2

MMSI = 0
LAT = 1
LONG = 2
COURSE = 3
SPEED = 4
RTIME = 5


def loadFile(filename):
    with open(filename,'rb') as f:
        b = pickle.load(f)
    return b

def keyToVals(key):
    import random
    location = ships[key][TRACKING]
    information = ships[key][INFO]
    return (key, location[LAT], location[LONG],random.randint(1,5), location[COURSE], location[SPEED], location[RTIME])




ships = loadFile("bestPickleEver0.txt")
print(len(ships))
print(ships)
# SELECT mmsi, lat, lon, class, course, speed, rtime  FROM ships_view
# initInsert = "INSERT INTO ships_view(mmsi, lat, lon, class, course, speed, rtime) values"
# l = [keyToVals(key) for key in ships]
# dict = mmsi : [[     ]





from utils import safe_cast
from math import round
import sys

def get_dist2coast_dict(filename = 'data/dist2coast.txt'):
    locations=dict()
    with open(filename, 'r') as f:
        for line in f:
            lst = [safe_cast(word, float) for word in line.split()]
            if (len(lst) < 3):
                print('error - ', file=sys.stderr)
                continue
            lan = int(lst[0] * 100)
            lon = int(lst[1] * 100)
            dist = lst[2]
            locations[(lan, lon)] = dist
    return locations


def pos_to_04_res(lat, lon):
    return round(lat*(5/2))*0.4, round(lon*(5/2))*0.4

def dist2coast(dist2coast_dict, lat, lon):
    return dist2coast_dict(pos_to_04_res(lat, lon))

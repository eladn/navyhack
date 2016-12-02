from utils import safe_cast
import pickle as pkl
from numpy import around
from math import floor, ceil
import sys


def showLine(n):
	f = open('dist2coast.txt', 'r')
	i = 0
	for row in f:
		i += 1
		if (i < n): continue
		print(row)
		break


def old_get_dist2coast_dict(filename='data/dist2coast.txt'):
	locations=dict()
	with open(filename, 'r') as f:
		for line in f:
			lst = [safe_cast(word, float) for word in line.split()]
			if (len(lst) < 3):
				print('error - ', file=sys.stderr)
				continue
			lan = '{:.2f}'.format(lst[0]) #int(floor(lst[0]*25))
			lon = '{:.2f}'.format(lst[1]) #int(floor(lst[1]*25))
			dist = lst[2]
			locations[(lan, lon)] = dist
	return locations


def get_dist2coast(filename='data/dist2coast.txt'):
	locations=list()
	with open(filename, 'r') as f:
		for line in f:
			locations.append(safe_cast(line.split()[2], int, 0))
	return locations

def pos_to_04_res(lat, lon):
	return max(0, min(ceil(9000 * (-lon + 98.98) * 25 + (lat + 179.98) * 25), 40500000-1))
#'{:.2f}'.format(lat), '{:.2f}'.format(lon)  #int(floor(lat*25)), int(floor(lon*25))


def dist2coast(dist2coast_lst, lat, lon):
	return dist2coast_lst[pos_to_04_res(lat, lon)]


'''
def dist2coast(dist2coast_dict, lat, lon):
	if pos_to_04_res(lat, lon) not in dist2coast_dict:
		print('not found {}  lat:{} lon:{}'.format(pos_to_04_res(lat, lon), lat, lon))
		return 0
	return dist2coast_dict[pos_to_04_res(lat, lon)]
'''

if __name__ == '__main__':
	dist2coast_lst = get_dist2coast()
	with open('data/dist2coast_int.pkl', 'wb') as pf:
		#dist2coast_dict = get_dist2coast_dict()
		pkl.dump(dist2coast_lst, pf)

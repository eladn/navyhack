from utils import safe_cast
import pickle as pkl
import sys


def get_dist2coast_dict(filename='data/dist2coast.txt'):
	locations=dict()
	with open(filename, 'r') as f:
		for line in f:
			lst = [safe_cast(word, float) for word in line.split()]
			if (len(lst) < 3):
				print('error - ', file=sys.stderr)
				continue
			lan = int(lst[0]*25)
			lon = int(lst[1]*25)
			dist = lst[2]
			locations[(lan, lon)] = dist
	return locations


def pos_to_04_res(lat, lon):
	return round(lat*25), round(lon*25)


def dist2coast(dist2coast_dict, lat, lon):
	return dist2coast_dict(pos_to_04_res(lat, lon))


if __name__ == '__main__':
	with open('data/dist2coast.pkl', 'wb') as pf:
		dist2coast_dict = get_dist2coast_dict()
		pkl.dump(dist2coast_dict, pf)

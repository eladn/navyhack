from utils import safe_cast
import pickle as pkl
from numpy import around
from math import floor, ceil
import sys


def get_dist2coast_list(filename='data/dist2coast.txt'):
	locations=list()
	with open(filename, 'r') as f:
		for line in f:
			words = line.split()
			if len(words) < 3: continue
			locations.append(safe_cast(words[2], int, 0))
	return locations


def pos_to_04_res_idx(lat, lon):
	return max(0, min(9000 * ceil((-lon + 98.98) * 25) + ceil((lat + 179.98) * 25), 40500000-1))


def dist2coast(dist2coast_lst, lat, lon):
	return dist2coast_lst[pos_to_04_res_idx(lat, lon)]


if __name__ == '__main__':
	dist2coast_lst = get_dist2coast_list()
	with open('data/dist2coast_int.pkl', 'wb') as pf:
		pkl.dump(dist2coast_lst, pf)

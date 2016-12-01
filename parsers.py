# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 10:41:02 2016

@author: Gal
"""

from __future__ import division
import pickle
import os
from os.path import isfile, join


'''
HEADER:
 0 - mmsi
 1 - lat
 2 - lon
 3 - course
 4 - speed
 5 - reported_time
 FUTURE:
 6 - lable
'''
'''
VECTORS:
vectors[0] - target's number
vectors[0][0] - target's lat list
vectors[0][1] - target's lon list
vectors[0][2] - speed list
vectors[0][3] - avrage speed
vectors[0][4] - course list
vectors[0][5] - avrage course
vectors[0][6] - mmsi
'''


def createVectors(fileName):
   vectors = []
   with open (fileName,'rb') as f:
        b = dict(pickle.load(f))
        for row in b:
            tmp = []
            lat = []
            lon = []
            speed = []
            course = []
            
            for i in range(len(b[row][0])):
                #lat#
                lat.append(b[row][0][i][1])
                #long#
                lon.append(b[row][0][i][2])
                #speed#
                speed.append(b[row][0][i][4])
                #course#
                course.append(b[row][0][i][3])
            tmp.append(lat)
            tmp.append(lon)
            tmp.append(speed)
            tmp.append(sum(speed)/len(speed))
            tmp.append(course)
            tmp.append(sum(course)/len(course))
            tmp.append(row)
            if (len(b[row][1]) == 0):
                tmp.append("")
                tmp.append("")
            else:
                if(b[row][1][3] in["Not Available","Not available"]):
                    tmp.append("")
                else:
                    tmp.append(b[row][1][3])
                tmp.append(b[row][1][-2])
            vectors.append(tmp)
   return vectors


def collectFiles(folder=""):
    vectors = []
    onlyfiles  = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in onlyfiles:
        if (str(f)[:4] == "best"):
            vectors +=createVectors(str(f))
    return vectors

print(len(collectFiles()))
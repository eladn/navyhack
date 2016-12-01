# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 09:34:23 2016

@author: Gal
"""
from parsers import createUnlabledVectors, collectFiles
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pylab as plt

'''
points:
points[0] - target's number
points[0][0] - target's lat list
points[0][1] - target's lon list
points[0][2] - speed list
points[0][3] - avrage speed
points[0][4] - course list
points[0][5] - avrage course
points[0][6] - mmsi
points[0][7] - label
'''

def simplePlot(points = collectFiles("bestPickleEver.txt")):
    for i in range(len(points)):
        x = points[i][1]
        y = points[i][0]
        print (points[i][3])
        if (len(x) > 10 and points[i][3] !=0):
            print len(x), len(y), points[i][3]
            plt.figure(i)
            plt.title("mmsi: "+ str(points[i][6]))
            plt.plot(x,y) 
            

def speedClustering(points = collectFiles("bestPickleEver.txt"), 
                    clusters = 3 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):
            if (len(points[i][j][2]) >= 10):
                speeds.append(points[i][j][2][:5])
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]
    
    
def courseClustering(points = collectFiles("bestPickleEver.txt"), 
                    clusters = 3 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):
            if (len(points[i][j][4]) >= 10):
                speeds.append(points[i][j][4][:5])
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]
    
def speedAndCourse(points = collectFiles("bestPickleEver.txt"), 
                    clusters = 5 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):
            if (len(points[i][j][4]) >= 10 and len(points[i][j][2]) >= 10):
                speeds.append(np.diff(points[i][j][4][:5]) + np.diff(points[i][j][2][:5]))
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]


def locationVector(points = collectFiles("bestPickleEver.txt"), 
                    clusters = 5 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):
            if (len(points[i][j][0]) >= 10 and len(points[i][j][1]) >= 10):
                speeds.append(points[i][j][0][:10] + points[i][j][1][:10])
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]
    

def makeSupervisedData(points = collectFiles("bestPickleEver.txt")):
    
    
    

    

points = collectFiles("a")
#speedClustering(points)
#simplePlot(points)
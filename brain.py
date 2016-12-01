# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 09:34:23 2016

@author: Gal
"""
from parsers import createVectors, collectFiles
import numpy as np
from sklearn.cluster import KMeans
from sklearn import svm
from sklearn.metrics import confusion_matrix
from matplotlib import pylab as plt
import statistics
from dist2coast import *
from sklearn.model_selection import cross_val_score


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
points[0][8] - status
'''

def simplePlot(points):
    for i in range(len(points)):
        x = points[i][1]
        y = points[i][0]
        print (points[i][3])
        if (len(x) > 10 and points[i][3] !=0):
            print (len(x), len(y), points[i][3])
            plt.figure(i)
            plt.title("mmsi: "+ str(points[i][6]))
            plt.plot(x,y) 
            

def speedClustering(points,
                    clusters = 3 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):
            if (len(points[i][j][2]) >= 10):
                speeds.append(points[i][j][2][:5])
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]
    
    
def courseClustering(points,
                    clusters = 3 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):
            if (len(points[i][j][4]) >= 10):
                speeds.append(points[i][j][4][:5])
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]
    
def speedAndCourse(points,
                    clusters = 5 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):

            if (len(points[i][j][4]) >= 10 and len(points[i][j][2]) >= 10):
                speeds.append(np.diff(points[i][j][4][:5]) + np.diff(points[i][j][2][:5]))
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]

def createAlgoVector(points):
    # d = get_dist2coast_dict()
    x = lambda y:True if y[7] is not "" and len(y[4])>9 and len(y[2])>9 else False
    deriv = lambda l:[l[i] - l[i+1] for i in range(len(l)-1)]
    r = lambda vector:vector[4][:9]+vector[2][:9]+[statistics.variance(vector[4])]+[statistics.variance(vector[2])]\
                +vector[0][:9]+vector[1][:9]
    # +[dist2coast(d,vector[0][0],vector[1][0])]
    speeds = []
    labels = []
    for vector in points:
        if(x(vector)):
            speeds.append(r(vector))
            labels.append(vector[7])
    return speeds, labels

def runAlgo(vec,label):
    clf = svm.LinearSVC()
    scores = cross_val_score(clf, vec, label, cv=4)
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def locationVector(points,
                    clusters = 5 ):
    speeds = []
    for i in range(len(points)):
        for j in range(len(points[i])):
            if (len(points[i][j][0]) >= 10 and len(points[i][j][1]) >= 10):
                speeds.append(points[i][j][0][:10] + points[i][j][1][:10])
    X = np.array(speeds)
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(X)
    return [kmeans, X, clusters]

def makeLabeledDataChange(points):
       speeds = []
       for row in points:
           for shipVector in row:
               if(shipVector[7] is ""):
                   continue
               speeds.append(shipVector)
       return getSC(speeds)



       # points = collectFiles("a")
# speedClustering(points)
# simplePlot(points)
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
from sklearn.model_selection import train_test_split
from matplotlib import pylab as plt
import statistics
from dist2coast import *
from sklearn.linear_model import Lasso
from sklearn.model_selection import cross_val_score, cross_val_predict
from datetime  import timedelta
import pickle
from pickleloader import loadFile
from math import pow, tan

epsilon = 0.00001


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
points[0][9] - status
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
    print('start load dist2coast')
    with open('data/dist2coast.pkl', 'rb') as f:
        dist2coast_lst = pickle.load(f)
    print('end load dist2coast')

    filterVector = lambda y:True if y[7] is not "" and len(y[4])>50 and len(y[2])>50 and y[7] != 'Other' else False

    def deriv(l,t):
        return [((l[i] - l[i+1])/((t[i]-t[i+1])/timedelta(minutes=1))) for i in range(len(l)-1)]
    def gradient(x,y,t):
        return zip(deriv(x,t), deriv(y,t))  # list of pairs. each pair is the two partial-derivatives.
    def derivative_direction(x,y,t):
        return [0 if y < epsilon else tan(x/y) for x,y in gradient(x,y,t)]
    def derivative_magnitude(x,y,t):
        return [pow(x,2)+pow(y,2) for x,y in gradient(x,y,t)]
    def add_to_all(l, delta):
        return [item+delta for item in l]
    def courseToDeltaCourse(course_values):
        return [(course_values[i]-course_values[i+1])%360 for i in range(len(course_values)-1)]

    # TODO: make the function receive set of wanted features to calc.
    def calcVector(vector):
        return courseToDeltaCourse(vector[4][:50]) +\
            vector[2][:50]+\
            [statistics.variance(vector[4])]+\
            [statistics.variance(vector[2])]+ \
            add_to_all(vector[0][:50], -vector[0][0])+ \
            add_to_all(vector[1][:50], -vector[1][0]) + \
            [statistics.mean([dist2coast(dist2coast_lst, vector[0][idx], vector[1][idx]) for idx in range(0, len(vector[0])-1)])]

            # --------- some experimental examples: --------
            # stats of velocity vector (magnitude+direction):
            #   [statistics.mean(derivative_magnitude(vector[0][:49], vector[1][:49], vector[-1][:49]))]
            #   [statistics.variance(derivative_direction(vector[0][:49], vector[1][:49], vector[-1][:49]))]
            # distance to shore statics:
            #   [dist2coast(dist2coast_lst, vector[0][idx], vector[1][idx]) for idx in range(0, 30)]+ \
            #   [statistics.variance(deriv([dist2coast(dist2coast_lst, vector[0][idx], vector[1][idx]) for idx in range(0, 49)], vector[-1][:49]))]
            # maximal acceleration:
            #   [max(deriv(derivative_magnitude(vector[0], vector[1], vector[-1]), vector[-1]))]
            # maximal angular acceleration:
            #   [max(deriv(derivative_direction(vector[0], vector[1], vector[-1]), vector[-1]))]
            # course values deltas:
            #   courseToDCourse(vector[4][:50])
            # course derivative:
            #   [x%360 for x in deriv(vector[4][:50], vector[-1][:50])]

    vectors = []
    labels = []
    mmsi = []   # in order to export the test group and predicted labels to pickle
    for vector in points:
        if(filterVector(vector)):
            vectors.append(calcVector(vector))
            labels.append(vector[7])
            mmsi.append(vector[6])
    return vectors, labels, mmsi

def runAlgo(vec,label,mmsi):
    clf = svm.LinearSVC()
    x1,x2,y1,y2 = train_test_split(vec, label, test_size=0.4, random_state=0)

    # in order to export the test group and predicted labels to pickle
    xx1, xx2, yy1, test_ships_mmsi = train_test_split(vec, mmsi, test_size=0.4, random_state=0)

    # learn
    clf.fit(x1,y1)

    cvScore = cross_val_score(clf,x2,y2,cv=7)
    print("SVM Linear SVC %f"%clf.score(x2,y2))
    print("SVM Linear SVC with crossValidation", cvScore)

    predicted_labels = clf.predict(x2)

    # export the test group and predicted labels to pickle
    data = {'test_ships_mmsi': test_ships_mmsi, 'predicted_labels': predicted_labels}
    with open('test_results.pkl', 'wb') as f:
        pickle.dump(data, f)

    # clf = Lasso()
    # x1, x2, y1, y2 = train_test_split(vec, label, test_size=0.4, random_state=0)
    # cvScore = cross_val_score(clf, x1, y1)
    # print("SVM Linear SVC %f" % clf.score(x2, y2))
    # print("SVM Linear SVC with crossValidation %f" % cvScore)

    # scores = cross_val_score(clf, vec, label, cv=3)
    # print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


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
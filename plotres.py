# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 13:51:04 2016

@author: Gal
"""

from matplotlib import pylab as plt
import numpy as np
from brain import locationVector
from sklearn.metrics.pairwise import pairwise_distances_argmin


# We want to have the same colors for the same cluster from the
# MiniBatchKMeans and the KMeans algorithm. Let's pair the cluster centers per
# closest one.
def showResults(vectors, fun):
    fig = plt.figure(figsize=(8, 3))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.05, top=0.9)
    colors = ['#0061FF', '#FA00FF', '#002AFF', '#FF9900', '#FF0000']

    k_means, X, n_clusters = fun(vectors)
    k_means_cluster_centers = np.sort(k_means.cluster_centers_, axis=0)
    k_means_labels = pairwise_distances_argmin(X, k_means_cluster_centers)
    # KMeans
    ax = fig.add_subplot(1, 3, 1)
    for k, col in zip(range(n_clusters), colors):
        my_members = k_means_labels == k
        cluster_center = k_means_cluster_centers[k]
        ax.plot(X[my_members, 0], X[my_members, 1], 'w',
                markerfacecolor=col, marker='.')
        ax.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                markeredgecolor='k', markersize=6)
    ax.set_title('KMeans')
    ax.set_xticks(())
    ax.set_yticks(())

    #plt.text(-3.5, 1.8,  'train time: %.2fs\ninertia: %f' % (
     #   t_batch, k_means.inertia_))
import pickle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def findBestCluster(clust: list) -> int:
    return max(clust)

def cluster(data, ret_fn):
    clustering = KMeans(n_clusters=5, random_state=5)
    pickle.dump(clustering.fit(data), open(ret_fn, 'wb'))


    return clustering
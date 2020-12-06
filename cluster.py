import pickle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def findBestCluster(clust: list) -> int:
    dict_counts = {}
    for num in clust:
        if num not in dict_counts:
            dict_counts[num] = 1
        else:
            dict_counts[num] += 1

    max_key = max(dict_counts, key=dict_counts.get)
    return (max_key, dict_counts[max_key])

def cluster(data, ret_fn):
    clustering = KMeans(n_clusters=5, random_state=5)
    this_clust = clustering.fit(data) 
    pickle.dump(clustering.fit(data), open(ret_fn, 'wb'))
    # print("Cluster: {}".format(this_clust))

    return this_clust
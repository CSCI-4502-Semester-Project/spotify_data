import pipeline
import cluster
import setup
import os
import pandas as pd
import zipfile


if __name__ == '__main__':
    directory = 'data/Spotify/' #Est. directory to obtain features.json
    track_storage = 'data/track_features/' #Est. directory to store features

    setup.createDirectories()
    list_dfs = []
    for filename in os.listdir(directory): #Run feature pipeline code
        list_dfs.append(pipeline.pipe(filename, directory, track_storage, binary=False))

    for i in range(len(list_dfs)): #Iterate over sets of features
        filename = "out" + str(i) + ".zip"
        try:
            list_dfs[i].to_csv(filename, index=False) #Convert file
            
            with zipfile.ZipFile(filename, 'r') as zip_ref: #Unzip files
                zip_ref.extractall("data/CSVs/")
                if zip_ref:
                    os.remove(filename)

            csv_filename = "out" + str(i) + ".csv"
            os.chdir("data/CSVs") #Change current working directory

            os.rename(filename, csv_filename) #Convert filename to .csv
            
            path_to_store = "out" + str(i) + ".p"
            df = pd.read_csv(csv_filename)
            os.chdir("../..") #Revert back to original directory
            os.chdir("data/Pickles/")
            clust = cluster.cluster(df, path_to_store)
            os.chdir("../..")

            # print("Labels: {}".format(clust.labels_))
            best_clust = cluster.findBestCluster(clust.labels_)

            print("Best cluster found for playlist {} is: {}".format(csv_filename, best_clust))

        #Error checking
        except:
            print("Unable to convert file {} to .csv".format(filename))

    

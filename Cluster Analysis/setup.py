import os

#Code to create data directory setup
def createDirectories():

    if "data" not in os.listdir():
        os.mkdir("data")
    os.chdir("data/")

    if "CSVs" not in os.listdir():
        os.mkdir("CSVs")

    if "Pickles" not in os.listdir():
        os.mkdir("Pickles")
    
    if "Spotify" not in os.listdir():
        os.mkdir("Spotify")

    if "track_features" not in os.listdir():
        os.mkdir("track_features")


    os.chdir("../")
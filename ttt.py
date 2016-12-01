import pickle

d = {1:1,2:2,3:3,4:4}

with open("bestPickleEver.txt", "wb") as f:
    pickle.dump(d, f, 2)
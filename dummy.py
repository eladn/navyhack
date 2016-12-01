from brain import *
from plotres import *
from parsers import *
from pickleloader import *
p = collectFiles("")
vec, labels = createAlgoVector(p)
mapper = loadFile("vessel_type_to_ship_type.pkl")
t = lambda x:mapper[x] if x in mapper else "Other"
labels = list(map(t, labels))
# print(set(labels))
runAlgo(vec,labels)
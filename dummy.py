from brain import *
from plotres import *
from parsers import *
from pickleloader import *
p = collectFiles("")
vec, labels = createAlgoVector(p)
mapper = loadFile("")
labels = list(map(labels,))
# print(set(labels))
runAlgo(vec,labels)
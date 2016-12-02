from brain import *
from plotres import *
from parsers import *
from pickleloader import *
p = collectFiles("")
vec, labels = createAlgoVector(p)
mapper = loadFile("vessel_type_to_ship_type.pkl")
t = lambda x:mapper[x] if x in mapper else "Other"
labels = list(map(t, labels))
superD = {'Tanker':'Merchant', 'Base':'Base', 'Supply':'Merchant', 'Passenger':'Merchant', 'Army':'Army', 'Other':'Other', 'Speed':'Army', 'Cargo':'Merchant', 'Tow':'Small', 'Fishing':'Small', 'Container':'Merchant'}
t = lambda x:superD[x]
labels = list(map(t,labels))
print(set(labels))
# print(set(labels))
runAlgo(vec,labels)
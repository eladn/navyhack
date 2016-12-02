from brain import *
from plotres import *
from parsers import *
from pickleloader import *
p = collectFiles("")

# db&pickle save vessel_type grabbed from myshiptracking. here we map it to our reduced set of types (we call it ship type
vessels_type_to_ship_type_mapper_data = loadFile("vessel_type_to_ship_type.pkl")
map_vessel_type_to_ship_type = lambda x: \
    vessels_type_to_ship_type_mapper_data[x] if x in vessels_type_to_ship_type_mapper_data else "Other"
for vector in p:
    vector[7] = map_vessel_type_to_ship_type(vector[7])

vec, labels, mmsi = createAlgoVector(p)

# second mapping to types. so that we'll have only 4 types (including other)
second_ship_type_mapping = {'Tanker':'Merchant', 'Base':'Base', 'Supply':'Merchant', 'Passenger':'Merchant', 'Army':'Army', 'Other':'Other', 'Speed':'Army', 'Cargo':'Merchant', 'Tow':'Small', 'Fishing':'Small', 'Container':'Merchant'}
second_ship_type_mapper = lambda x: second_ship_type_mapping[x]
labels = list(map(second_ship_type_mapper, labels))
print(set(labels))

runAlgo(vec,labels,mmsi)
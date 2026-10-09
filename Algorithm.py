import pandas as pd 

def make_distance_lookup(distance_file):
    distance = pd.read_excel(distance_file)

    distance_lookup = {}
    for i in range(len(distance)):
        start = distance.loc[i,'start']
        end = distance.loc[i,'end']
        line = distance.loc[i,'line']

        if pd.isna(line):
            km = float(distance.loc[i,'distance_m'] / 1000)
            minutes = int(distance.loc[i,'max_travel_time'])
            distance_lookup[(start,end)] = (km,minutes)
    return distance_lookup

#lookup = make_distance_lookup('DistanceMatrix.xlsx')
#print(lookup[('ehvbst','ehvbst')])

def get_drive()
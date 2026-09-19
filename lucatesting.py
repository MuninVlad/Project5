import pandas as pd


bp = pd.read_excel('Bus Planning.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
t = pd.read_excel('Timetable.xlsx')

#Testing datasets
invalid_time = dm[dm['min_travel_time'] > dm['max_travel_time']]
neg_values = dm[(dm['min_travel_time'] < 0) | (dm['max_travel_time'] < 0) | (dm['distance_m'] < 0)]
print(len(invalid_time))
print(len(neg_values))

#idle times with zero minutes
zero_dur = bp[bp['end time'] == bp['start time']]
print(len(zero_dur))


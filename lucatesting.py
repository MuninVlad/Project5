import pandas as pd


bp = pd.read_excel('Bus Planning.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
t = pd.read_excel('Timetable.xlsx')

#Testing datasets in distancematrix
def distance_matrix(dm):
    invalid_time = dm[dm['min_travel_time'] > dm['max_travel_time']]
    neg_values = dm[(dm['min_travel_time'] < 0) | (dm['max_travel_time'] < 0) | (dm['distance_m'] < 0)]
    try:

        if invalid_time:
            return len(invalid_time)
    except:
        print(f'error invalid distance matrix\nFound{len(neg_values)} negative values')

    # print(len(neg_values))

#idle times with zero minutes
def idle_with_zero_minutes(bp):
    zero_dur = bp[bp['end time'] == bp['start time']]
    print(len(zero_dur))


#charging with positive or zero energy
def consumption_during_chargin(bp):
    invalid_charging = bp[(bp['activity'] == 'charging') & (bp['energy consumption'] >= 0)]
    invalid_charging['excel_row'] = invalid_charging.index + 2  # because excel rows are different than pandas rows
    print(invalid_charging[['excel_row', 'activity', 'energy consumption']])


#material/service trips with negative energy
def trips_with_negative_consumption(bp):
    invalid_trips = bp[(bp['activity'].isin(['service trip', 'material trip'])) & (bp['energy consumption'] < 0)]
    invalid_trips['excel_rows'] = invalid_trips.index + 2
    print(invalid_trips[['excel_rows','activity','energy consumption']])
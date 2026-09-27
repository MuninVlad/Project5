import pandas as pd


bp = pd.read_excel('Bus Planning.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
t = pd.read_excel('Timetable.xlsx')

#test status: success
def check_columns(bp):
    df_columns = bp.columns
    required_columns = ['start location','end location', 'start time', 'end time', 'activity', 'line' ,'energy consumption', 'bus']
    result = all(item in df_columns for item in required_columns)
    return result


#test status: success
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


#test status: success
#idle times with zero minutes
def idle_with_zero_minutes(bp):
    zero_dur = bp[bp['end time'] == bp['start time']]
    return zero_dur
    # print(len(zero_dur))


#test status: success
#charging with positive or zero energy
def consumption_during_chargin(bp):
    invalid_charging = bp[(bp['activity'] == 'charging') & (bp['energy consumption'] >= 0)]
    invalid_charging['excel_row'] = invalid_charging.index + 2  # because excel rows are different than pandas rows
    return invalid_charging[['excel_row', 'activity', 'energy consumption']]
    # print(invalid_charging[['excel_row', 'activity', 'energy consumption']])


#test status: fail
#material/service trips with negative energy
def trips_with_negative_consumption(bp):
    invalid_trips = bp[(bp['activity'].isin(['service trip', 'material trip'])) & (bp['energy consumption'] < 0)]
    invalid_trips['excel_rows'] = invalid_trips.index + 2
    return invalid_trips[['excel_rows','activity','energy consumption']]
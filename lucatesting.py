import pandas as pd


bp = pd.read_excel('Bus Planning.xlsx')
dm = pd.read_excel('DistanceMatrix.xlsx')
t = pd.read_excel('Timetable.xlsx')

### BUS PLANNING TESTS 
#test status: success
def check_columnsbp(bp):
    df_columns = bp.columns
    required_columns = ['start location','end location', 'start time', 'end time', 'activity', 'line' ,'energy consumption', 'bus']
    result = all(item in df_columns for item in required_columns)
    return result

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


### DISTANCE MATRIX TESTS

#test status: success
#Testing datasets in distancematrix

def check_columnsdm(dm):
    df_columns = dm.columns
    required_columns = ['start','end', 'min_travel_time', 'max_travel_time', 'distance_m', 'line']
    result = all(item in df_columns for item in required_columns)
    return result


def time_matrix(dm):
    # invalid_time = dm[dm['min_travel_time'] > dm['max_travel_time']]
    neg_values = dm.index[(dm['min_travel_time'] < 0) | (dm['max_travel_time'] < 0)]
    return neg_values

# test status:
# distance is minus 
def minus_distance(dm):
    neg_distance = dm.index[dm['distance_m'] < 0]
    return neg_distance


# test if activity is a trip but start and end are the same
def trip_with_the_same_start_and_end(bp):
    active_trips = bp[bp['activity'].isin(['material trip', 'service trip'])]
    error_dest_trips = active_trips[active_trips['start location'] == active_trips['end location']]
    return error_dest_trips

def data_submitted_successfully(file_path):
    if pd.read_excel(file_path):
        return True
    else:
        return False

#no nulls in the planning 
def check_nulls(bp):
    # number of nulls in all columns except line column
    without_line = bp.drop(columns='line')
    num_of_nulls = without_line.isnull().sum().sum()   
    return num_of_nulls

# no duplicate trips
def check_duplicates(bp):
    num_duplicates = bp.duplicated().sum()
    return num_duplicates
    
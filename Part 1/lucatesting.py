import pandas as pd
from datetime import time 
from Algorithm import StateOfHealth


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

def invalid_trip_time(bp):
    start = pd.to_datetime(bp['start time'].astype(str), format='mixed').dt.time
    end = pd.to_datetime(bp['end time'].astype(str), format='mixed').dt.time
    four_am = time(4, 0)

    overnight = (start > four_am) & (end <= four_am)

    return bp[(start > end) & ~overnight]
    
    # invalid_times = bp[bp['start time'] > bp['end time']]
    # return invalid_times



### DISTANCE MATRIX TESTS

#test status: success
#Testing datasets in distancematrix

def check_columnsdm(dm):
    df_columns = dm.columns
    required_columns = ['start','end', 'min_travel_time', 'max_travel_time', 'distance_m', 'line']
    result = all(item in df_columns for item in required_columns)
    return result


# def time_matrix(dm):
#     # invalid_time = dm[dm['min_travel_time'] > dm['max_travel_time']]
#     neg_values = dm.index[(dm['min_travel_time'] < 0) | (dm['max_travel_time'] < 0)]
#     return neg_values

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
    

### FEASIBILITY CHECKS

# times before 04:00 belong to the next day (same as Algorithm.py)
# empty or broken times become NaN so they are skipped
def time_to_minutes(value):
    text = str(value)
    try:
        minutes = int(text[0:2]) * 60 + int(text[3:5])
    except ValueError:
        return float('nan')
    if minutes < 240:
        minutes += 1440
    return minutes

# adds start/end in minutes and sorts every bus by start time
def plan_in_time_order(bp):
    plan = bp.copy()
                                # + 2 excel header and pandas starts from 0
    plan['excel_row'] = plan.index + 2
    plan['start_min'] = plan['start time'].apply(time_to_minutes)
    plan['end_min'] = plan['end time'].apply(time_to_minutes)
    plan = plan.dropna(subset=['start_min', 'end_min'])
    plan.loc[plan['end_min'] < plan['start_min'], 'end_min'] += 1440
    return plan.sort_values(['bus', 'start_min', 'end_min'], kind='stable')

#bus scheduled for two activities at the same time
def overlapping_activities(bp):
    plan = plan_in_time_order(bp)
    previous_end = plan.groupby('bus')['end_min'].shift()
    overlaps = plan[plan['start_min'] < previous_end]
    return overlaps[['excel_row', 'bus', 'start time', 'end time', 'activity']]

#bus starts an activity somewhere other than where the previous one ended
def location_mismatch(bp):
    plan = plan_in_time_order(bp)
    plan['previous end'] = plan.groupby('bus')['end location'].shift()
    mismatch = plan[plan['previous end'].notna() & (plan['start location'] != plan['previous end'])]
    return mismatch[['excel_row', 'bus', 'previous end', 'start location', 'start time', 'activity']]


#battery below 10% of usable capacity
def battery_below_minimum(bp, battery_size=300, soh = StateOfHealth, start_soc=0.9):
    usable = battery_size * soh
    lowest = usable * 0.1
    plan = plan_in_time_order(bp)
    plan['battery'] = usable * start_soc - plan.groupby('bus')['energy consumption'].cumsum()
    too_low = plan[plan['battery'] < lowest]
    return too_low[['excel_row', 'bus', 'start time', 'activity', 'battery']]

#charging shorter than 15 minutes
def short_charging(bp, min_minutes=15):
    plan = plan_in_time_order(bp)
    plan['duration'] = plan['end_min'] - plan['start_min']
    short = plan[(plan['activity'] == 'charging') & (plan['duration'] < min_minutes)]
    return short[['excel_row', 'bus', 'start time', 'end time', 'duration']]

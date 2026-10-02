import pandas as pd
import numpy as np 
# import time lib. to start time from zero 
import datetime  

dm = pd.read_excel('DistanceMatrix.xlsx')
bp = pd.read_excel('Bus Planning.xlsx')

battery_capacity = 300
SoH = 0.85
margin_SoH = 0.1
charge_rate_less_than_90 = 450 
charge_rate_more_than_90 = 60 
# find real capacity of the battery based on SoH and margin_SoH
real_capacity = battery_capacity * SoH * (1 - margin_SoH)
minimum_soc = 0.1 * real_capacity
idle_consumption_per_hour = 5


# create buses data frame 
def create_buses_df(num_of_busses):
    # returns bus_num, current stop, SoC, status
    #zero is available, one is busy
    return pd.DataFrame({
        'bus_num': range(1, num_of_busses + 1),
        'current_stop': 'garage',
        'SoC': 100.0,
        'status': 0,
        #start with zero time for all buses
        'time': time_zero , 
        'time2': datetime.datetime.combine(datetime.date.today(), datetime.time.min)

    })

# get distance for a trip 
def get_distance(trip):
    distance = dm[(dm['start'] == trip['start']) & (dm['end'] == trip['end'])]['distance_m'].iloc[0]
    return distance

def travel_time(distance_matrix):
    distance_matrix['average_travel_time'] = distance_matrix[['min_travel_time', 'max_travel_time']].mean()

#find consumption for all distinct trips in bus planning data frame bp
def find_consumption_for_all_trips(bp):
    distinct_trips = bp[['start location', 'end location', 'activity', 'line','energy consumption']].drop_duplicates()  
    distinct_trips.drop(distinct_trips[distinct_trips['activity'] == 'charging'].index, inplace=True)
    consumption_list = []
    for index, row in distinct_trips.iterrows():
        start = row['start location']
        end = row['end location']
        trip_type = row['activity']
        line = row['line']

        consumption = distinct_trips[(distinct_trips['start location'] == start) &(distinct_trips['activity'] == trip_type) &(distinct_trips['end location'] == end)]['energy consumption'].iloc[0]
        consumption_list.append({'start': start, 'end': end, 'consumption': consumption , 'activity': trip_type, 'line': line})
    return pd.DataFrame(consumption_list)

consumption_df = find_consumption_for_all_trips(bp)

#fint consumption between two stops using bus planning data frame bp
def find_consumption_between_two_stops(start, end):
    consumption = consumption_df[(consumption_df['start location'] == start) & (consumption_df['end location'] == end)]['energy consumption'].iloc[0]
    return consumption

    #     consumption = distinct_trips[(distinct_trips['start location'] == start) & (distinct_trips['line']==line) &(distinct_trips['activity'] == trip_type) &(distinct_trips['end location'] == end)]['energy consumption'].iloc[0]
    #     consumption_list.append({'start': start, 'end': end, 'consumption': consumption , 'activity': trip_type, 'line': line})
    # return pd.DataFrame(consumption_list)

# find available buses 
def find_available_buses(bdf):
    #buses data frame bdf
    return(bdf[bdf['status'] == 0])

# find earliest trip 
def next_trip(time_table):
    #time table tb
    tb = pd.DataFrame(time_table)
    tb.sort_values(['departure_time'], inplace=True)
    #return only the first pending trip
    #start - departure_time	- end - line
    return tb.head(1) # returns trip object 

# chech bus ability to take a trip or find bus for a trip 
def find_bus_for_next_trip(available_buses, trip):

    for bus in available_buses():   

        # get current stop of the bus
        current_stop = bus['current_stop'] 

        #check if the bus is at the same stop as the trip start
        if trip['end'] == current_stop:

            # get current SoC of the bus
            current_soc = bus['SoC']
            
            # get next trip's consumption and then consumption to garage
            trip_consumption = find_consumption_between_two_stops(current_stop, trip['end'])
            consumption_to_garage = find_consumption_between_two_stops(trip['end'], 'garage')            
            is_able = current_soc - (trip_consumption + consumption_to_garage) >= minimum_soc

            if is_able:
                return bus
            else:
                return None

#assign bus a trip
def assign_bus_to_trip(bus, trip):
    #check if find bus for next trip returns a bus number or None
    if bus is not None:
        #update bus status to busy
        bus['status'] = 1
        #update bus current stop to trip end
        bus['current_stop'] = trip['end']
        #update bus SoC to new SoC after trip
        trip_consumption = find_consumption_between_two_stops(bus['current_stop'], trip['end'])
        bus['SoC'] -= trip_consumption
        return bus

# check if a bus can be made idle, 
def can_bus_idle(bus):
    #get current stop and SoC of the bus
    current_stop = bus['current_stop']
    current_soc = bus['SoC']

    #find the longest trip from the current stop and its consumption (worst case scenario)
    all_cunsumptions = find_consumption_for_all_trips(bp)
    cons_from_current_step = all_cunsumptions[all_cunsumptions['start'] == current_stop]
    highest_consumption = cons_from_current_step['consumption'].max()
    consumption_to_garage = find_consumption_between_two_stops(highest_consumption['end'], 'garage')
                                #for safety add an hour of idle
    can_idle = current_soc - (highest_consumption + consumption_to_garage + idle_consumption_per_hour) >= minimum_soc
    if can_idle:
        return True
    else:
        return False



print('run successfully')
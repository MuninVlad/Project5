import pandas as pd 
import math

ENERGY_PER_KM = 1.2           
IDLE_PER_MIN = 5 / 60         
CHARGE_PER_MIN = 450 / 60     
MIN_CHARGE_TIME = 15          
EXTRA_WAIT = 0               
GARAGE = 'ehvgar'

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


def get_drive(lookup,start,end):
    if start == end:
        return (0,0)
    return lookup[start,end]

lookup = make_distance_lookup('DistanceMatrix.xlsx')
result = get_drive(lookup,'ehvbst','ehvbst')


def battery_limits(battery_size,soh):
    usable = battery_size * soh
    lowest = usable * 0.1
    highest = usable * 0.9
    start_charge = usable * 0.9
    return usable,lowest,highest,start_charge

def time_to_minutes(text):
    hours = int(text[0:2]) * 60
    minutes = int(text[3:5])
    return hours + minutes

def load_trips(timetable_file, distance_file):
    timetable = pd.read_excel(timetable_file)
    distance = pd.read_excel(distance_file)

    
    trip_info = {}
    for i in range(len(distance)):
        line = distance.loc[i, 'line']
        if not pd.isna(line):                     
            key = (distance.loc[i, 'start'], distance.loc[i, 'end'], int(line))
            km = float(distance.loc[i,'distance_m']/1000)
            duration = distance.loc[i,'max_travel_time']
            trip_info[key] = (km, duration)

   
    trips = []
    for i in range(len(timetable)):
        start = timetable.loc[i,'start']
        end = timetable.loc[i,'end']
        line = int(timetable.loc[i,'line'])
        departure = time_to_minutes(timetable.loc[i,'departure_time'])

        if departure < 240:                         
            departure = departure + 1440                         

        km, duration = trip_info[(start,end,line)]               

        trip = {'start': start, 'end': end, 'line': line,
                'departure': departure, 'km': km, 'duration': duration}
        trips.append(trip)

    
    trips.sort(key=lambda t: t['departure'])

    return trips


def find_free_bus(buses, trip, lookup, lowest):
    chosen_bus = None                                  
    shortest_empty = 999999                             

    for bus in buses:                                  
        empty_km, empty_minutes = get_drive(lookup, bus['position'], trip['start'])        
        waiting = trip['departure'] - (bus['free_from'] + empty_minutes)                    
        energy_needed = (empty_km + trip['km']) * ENERGY_PER_KM + (waiting + EXTRA_WAIT) * IDLE_PER_MIN   
        home_km, home_minutes = get_drive(lookup, trip['end'], GARAGE)       
        energy_home = home_km * ENERGY_PER_KM

        if waiting >= 0 and bus['battery'] - energy_needed - energy_home >= lowest:                           
            if chosen_bus is None or empty_km < shortest_empty or (empty_km == shortest_empty and bus['battery'] < chosen_bus['battery']):   
                chosen_bus = bus                                   
                shortest_empty = empty_km                                 

    return chosen_bus

def create_new_bus(buses, trip, lookup, start_charge):
    drive_km, drive_minutes = get_drive(lookup, GARAGE, trip['start'])   

    new_bus = {'id': len(buses) + 1 ,
               'position': GARAGE,
               'free_from': trip['departure'] - drive_minutes,
               'battery': start_charge,
               'route': []}

    buses.append(new_bus)
    return new_bus

def assign_trip(bus, trip, lookup):

    
    if bus['position'] != trip['start']:
        drive_km, drive_minutes = get_drive(lookup, bus['position'], trip['start'])
        energy = drive_km * ENERGY_PER_KM
        bus['route'].append({'start': bus['position'], 'end': trip['start'],
                             'start_time': bus['free_from'], 'end_time': bus['free_from'] + drive_minutes,
                             'activity': 'material trip', 'line': None,
                             'energy': energy})
        bus['battery'] = bus['battery'] - energy
        bus['free_from'] = bus['free_from'] + drive_minutes
        bus['position'] = trip['start']

  
    if bus['free_from'] < trip['departure']:
        waiting = trip['departure'] - bus['free_from']
        energy = IDLE_PER_MIN * waiting
        bus['route'].append({'start': trip['start'], 'end': trip['start'],
                             'start_time': bus['free_from'], 'end_time': trip['departure'],
                             'activity': 'idle', 'line': None,
                             'energy': energy})
        bus['battery'] = bus['battery'] - energy
        bus['free_from'] = trip['departure']

    
    energy = trip['km'] * ENERGY_PER_KM
    bus['route'].append({'start': trip['start'], 'end': trip['end'],
                         'start_time': trip['departure'], 'end_time': trip['departure'] + trip['duration'],
                         'activity': 'service trip', 'line': trip['line'],
                         'energy': energy})
    bus['battery'] = bus['battery'] - energy
    bus['free_from'] = trip['departure'] + trip['duration']
    bus['position'] = trip['end']

def charge_bus(bus, trip, lookup, lowest, highest):

    
    to_garage_km, to_garage_minutes = get_drive(lookup, bus['position'], GARAGE)
    battery_on_arrival = bus['battery'] - to_garage_km * ENERGY_PER_KM
    arrival = bus['free_from'] + to_garage_minutes

    
    to_start_km, to_start_minutes = get_drive(lookup, GARAGE, trip['start'])
    latest_end = trip['departure'] - to_start_minutes

    
    charge_end = arrival + (highest - battery_on_arrival) / CHARGE_PER_MIN
    if charge_end > latest_end:
        charge_end = latest_end
    if charge_end < arrival + MIN_CHARGE_TIME:
        charge_end = arrival + MIN_CHARGE_TIME
    charge_end = math.ceil(charge_end)

    
    battery_after = battery_on_arrival + (charge_end - arrival) * CHARGE_PER_MIN
    if battery_after > highest:
        battery_after = highest

    waiting = trip['departure'] - (charge_end + to_start_minutes)
    energy_needed = (to_start_km + trip['km']) * ENERGY_PER_KM + (waiting + EXTRA_WAIT) * IDLE_PER_MIN
    home_km, home_minutes = get_drive(lookup, trip['end'], GARAGE)
    energy_home = home_km * ENERGY_PER_KM

    
    if battery_on_arrival >= lowest and battery_on_arrival < highest and charge_end <= latest_end and battery_after - energy_needed - energy_home >= lowest:
        if bus['position'] != GARAGE:
            bus['route'].append({'start': bus['position'], 'end': GARAGE,
                                 'start_time': bus['free_from'], 'end_time': arrival,
                                 'activity': 'material trip', 'line': None,
                                 'energy': to_garage_km * ENERGY_PER_KM})
        bus['route'].append({'start': GARAGE, 'end': GARAGE,
                             'start_time': arrival, 'end_time': charge_end,
                             'activity': 'charging', 'line': None,
                             'energy': -(battery_after - battery_on_arrival)})
        bus['position'] = GARAGE
        bus['free_from'] = charge_end
        bus['battery'] = battery_after
        return True

    return False

def build_plan(trips, lookup, lowest,highest, start_charge):
    buses = []

    
    for trip in trips:
        bus = find_free_bus(buses, trip, lookup, lowest)
        if bus is None:
            for b in buses:
                if charge_bus(b, trip, lookup, lowest, highest):
                    bus = b
                    break
        if bus is None:
            bus = create_new_bus(buses, trip, lookup, start_charge)
        assign_trip(bus, trip, lookup)                     

    
    for bus in buses:
        if bus['position'] != GARAGE:
            drive_km, drive_minutes = get_drive(lookup, bus['position'], GARAGE)
            energy = drive_km * ENERGY_PER_KM
            bus['route'].append({'start': bus['position'], 'end': GARAGE,
                                 'start_time': bus['free_from'], 'end_time': bus['free_from'] + drive_minutes,
                                 'activity': 'material trip', 'line': None,
                                 'energy': energy})
            bus['battery'] = bus['battery'] - energy
            bus['free_from'] = bus['free_from'] + drive_minutes
            bus['position'] = GARAGE

    
    number_of_buses = len(buses)
    return buses, number_of_buses


# exporting to Excel file
def minutes_to_time(minutes):
    minutes = minutes % 1440
    hours = minutes // 60
    mins = minutes % 60
    return f'{hours:02d}:{mins:02d}:00'

def save_plan(buses, file_name):
    rows = []
    for bus in buses:
        for row in bus['route']:
            rows.append({'start location': row['start'],
                         'end location': row['end'],
                         'start time': minutes_to_time(row['start_time']),
                         'end time': minutes_to_time(row['end_time']),
                         'activity': row['activity'],
                         'line': row['line'],
                         'energy consumption': row['energy'],
                         'bus': bus['id']})
    table = pd.DataFrame(rows)
    table.to_excel(file_name, index=False)

lookup = make_distance_lookup('DistanceMatrix.xlsx')
usable, lowest, highest, start_charge = battery_limits(300, 0.85)
trips = load_trips('Timetable.xlsx', 'DistanceMatrix.xlsx')
buses, number_of_buses = build_plan(trips, lookup, lowest, highest, start_charge)
save_plan(buses, 'our_bus_plan.xlsx')
print('Bus plan saved to our_bus_plan.xlsx with', number_of_buses, 'buses')
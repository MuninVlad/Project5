import pandas as pd 
ENERGY_PER_KM = 1.2           # кВт·ч на км (из Excel клиента)
IDLE_PER_MIN = 5 / 60         # кВт·ч в минуту, пока автобус стоит
CHARGE_PER_MIN = 450 / 60     # кВт·ч в минуту при зарядке (7.5)
MIN_CHARGE_TIME = 15          # минут
EXTRA_WAIT = 0                # минут
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
#print(result)

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
            km = distance.loc[i,'distance_m']/1000
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
trips = load_trips('Timetable.xlsx','DistanceMatrix.xlsx')

def find_free_bus(buses, trip, lookup, lowest):
    chosen_bus = None                                  
    shortest_empty = 999999                             

    for bus in buses:                                  
        empty_km, empty_minutes = get_drive(lookup, bus['position'], trip['start'])        # 16: от автобуса до начала рейса
        waiting = trip['departure'] - (bus['free_from'] + empty_minutes)                    # 17
        energy_needed = (empty_km + trip['km']) * ENERGY_PER_KM + (waiting + EXTRA_WAIT) * IDLE_PER_MIN   # 18
        home_km, home_minutes = get_drive(lookup, trip['end'], GARAGE)       # 19: от конца рейса до гаража
        energy_home = home_km * ENERGY_PER_KM

        if waiting >= 0 and bus['battery'] - energy_needed - energy_home >= lowest:                           # 20
            if chosen_bus is None or empty_km < shortest_empty or (empty_km == shortest_empty and bus['battery'] < chosen_bus['battery']):   # 21
                chosen_bus = bus                                    # 22
                shortest_empty = empty_km                                 # 23

    return chosen_bus

def create_new_bus(buses, trip, lookup, start_charge):
    drive_km, drive_minutes = get_drive(lookup, GARAGE, trip['start'])    # от гаража до начала рейса

    new_bus = {'id': len(buses) + 1 ,
               'position': GARAGE,
               'free_from': trip['departure'] - drive_minutes,
               'battery': start_charge,
               'route': []}

    buses.append(new_bus)
    return new_bus
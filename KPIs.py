import pandas as pd
from datetime import datetime


def calculations_KPIs(bus_plan, distance_matrix):

    planning = pd.read_excel(bus_plan)
    distance = pd.read_excel(distance_matrix)

    number_buses = planning['bus'].nunique() # number of buses

    total_energy = 0 # total energy consumption
    for i in range(len(planning)):
        if planning.loc[i,'energy consumption'] > 0:
            total_energy += planning.loc[i,'energy consumption']

    distance_lookup = {}
    for j in range(len(distance)):
        d_start = distance.loc[j, 'start']
        d_end = distance.loc[j, 'end']
        d_line = distance.loc[j, 'line']

        if pd.isna(d_line):
            d_line = None

        key = (d_start, d_end, d_line)
        distance_lookup[key] = distance.loc[j, 'distance_m']

    deadhead_distance = 0  # the material trip distance

    for i in range(len(planning)):
        activity = planning.loc[i, 'activity']   
        if activity == 'material trip':
            start = planning.loc[i, 'start location']
            end = planning.loc[i, 'end location']

            key = (start, end, None)

            if key in distance_lookup:
                distance_m = distance_lookup[key]
                deadhead_distance += distance_m

    deadhead_distance_km = deadhead_distance / 1000

    total_idle_time = 0 # total idle time 
    for i in range(len(planning)):
        activity = planning.loc[i,'activity']
        if activity == 'idle':
            start = datetime.strptime(planning.loc[i,'start time'],"%H:%M:%S")
            end = datetime.strptime(planning.loc[i,'end time'],"%H:%M:%S")
            difference = end - start
            minutes = difference.total_seconds() / 60
            if minutes < 0:
                minutes += 1440
            total_idle_time += minutes

    return number_buses,total_energy,deadhead_distance_km,total_idle_time

number_buses, total_energy, deadhead_km, idle_time = calculations_KPIs(
    'Bus Planning.xlsx', 'DistanceMatrix.xlsx')

print(f'The number of buses = {number_buses}')
print(f'Total energy consumption = {total_energy}')
print(f'Deadhead distance = {deadhead_km:.2f} km')
print(f'Total idle time = {idle_time:.0f} minutes')
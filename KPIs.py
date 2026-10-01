import pandas as pd

df_planning = pd.read_excel('Bus Planning.xlxs')

number_buses = df_planning['bus'].nunique() # number of buses
total_energy = 0 # total energy consumption
for i in range(len(df_planning)):
    if df_planning['energy consumption'] > 0:
        total_energy += df_planning['energy consumption']

average_energy_cons = total_energy / number_buses # average energy consumption per bus 


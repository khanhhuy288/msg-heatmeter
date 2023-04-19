import pandas as pd
import plotly.graph_objs as go
import numpy as np
import holidays

filename = "Trend-2021-09-09_08-02_30.csv"

# Read the CSV file and select columns
fields = ["Arbeit [MWh]", "Leistung [kW]", "Außentemperatur [°C]", "Zeit", "Prim. Vorlauf [°C]",
          "Prim. Rücklauf [°C]", "Rücklauf 1 [°C]", "Rücklauf 2 [°C]", "Vorlauf 1 [°C]"]

df = pd.read_csv("Trend-2021-09-09_08-02_30.csv", delimiter=";", usecols=fields)

# Rename columns
df.rename(columns={'Leistung [kW]': 'Leistung', 'Außentemperatur [°C]': 'Außentemperatur',
                   "Prim. Vorlauf [°C]": "Prim. Vorlauf",
                   "Prim. Rücklauf [°C]": "Prim. Rücklauf",
                   "Rücklauf 1 [°C]": "Rücklauf 1",
                   "Rücklauf 2 [°C]": "Rücklauf 2",
                   "Vorlauf 1 [°C]": "Vorlauf 1"}, inplace=True)

df.rename(columns={"Arbeit [MWh]": "Arbeit"}, inplace=True)

# Convert columns to appropriate data types
df['Leistung'] = df['Leistung'].str.replace(',', '.').astype(float)
df['Außentemperatur'] = df['Außentemperatur'].str.replace(',', '.').astype(float)
df['Rücklauf 1'] = df['Rücklauf 1'].str.replace(',', '.').astype(float)
df['Rücklauf 2'] = df['Rücklauf 2'].str.replace(',', '.').astype(float)
df['Vorlauf 1'] = df['Vorlauf 1'].str.replace(',', '.').astype(float)
df['Zeit'] = pd.to_datetime(df['Zeit'], format='%d.%m.%Y %H:%M:%S')
df['Arbeit'] = df['Arbeit'].str.replace(',', '.').astype(float)

# Filter Arbeit > 0
df = df[df['Arbeit'] > 0]

# Set the index of the DataFrame to the "Zeit" column
df.set_index('Zeit', inplace=True)

# Filter to only include Heizperiode (01.10 - 30.04)
df = df.loc[(df.index.month >= 10) | (df.index.month <= 4)]

# ----- Process Temperature Data -----
# Calculate mean temperature for each hour
temps = df.groupby(df.index.hour).mean()
vorlauf_temp = temps['Prim. Vorlauf']
rucklauf_temp = temps['Prim. Rücklauf']
outside_temp = temps['Außentemperatur']
rucklauf_1_temp = temps['Rücklauf 1']
rucklauf_2_temp = temps['Rücklauf 2']
vorlauf_1_temp = temps['Vorlauf 1']

# Define the traces for each line
hovertemplate = '%{y:.1f}°C'
hour_values = list(range(0, 24))
trace_vorlauf = go.Scatter(x=hour_values, y=vorlauf_temp,
                           mode='lines', name='Vorlauf Temperature',
                           hovertemplate=hovertemplate)
trace_vorlauf_1 = go.Scatter(x=hour_values, y=vorlauf_1_temp,
                             mode='lines', name='Vorlauf 1 Temperature',
                             hovertemplate=hovertemplate)
trace_rucklauf = go.Scatter(x=hour_values, y=rucklauf_temp,
                            mode='lines', name='Rucklauf Temperature',
                            hovertemplate=hovertemplate)
trace_rucklauf_1 = go.Scatter(x=hour_values, y=rucklauf_1_temp,
                              mode='lines', name='Rucklauf 1 Temperature',
                              hovertemplate=hovertemplate)
trace_rucklauf_2 = go.Scatter(x=hour_values, y=rucklauf_2_temp,
                              mode='lines', name='Rucklauf 2 Temperature',
                              hovertemplate=hovertemplate)
trace_outside = go.Scatter(x=hour_values, y=outside_temp,
                           mode='lines', name='Outside Temperature',
                           hovertemplate=hovertemplate)

# Define the data and layout
data = [trace_vorlauf, trace_vorlauf_1, trace_rucklauf, trace_rucklauf_1, trace_rucklauf_2, trace_outside]
layout = go.Layout(title=dict(text='Hourly Temperature', x=0.5),
                   xaxis=dict(title='Time (Hour)', dtick=1),
                   yaxis=dict(title='Temperature (°C)'))

# Create the figure and plot it
fig = go.Figure(data=data, layout=layout)
fig.update_layout(showlegend=True, height=600, hovermode='x')
fig.show()
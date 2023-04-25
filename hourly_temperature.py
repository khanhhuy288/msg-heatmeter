import pandas as pd
import plotly.graph_objs as go

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
temp_cols = ['Prim. Vorlauf', 'Prim. Rücklauf',
             'Außentemperatur', 'Rücklauf 1', 'Rücklauf 2', 'Vorlauf 1']
temp_data = [(temps[col], col) for col in temp_cols]

# ----- Temperature Chart -----
# Define the traces for each line
hour_values = list(range(0, 24))
hovertemplate = '%{y:.1f}°C'

fig = go.Figure()

for temp, name in temp_data:
    fig.add_trace(
        go.Scatter(
            x=hour_values,
            y=temp,
            mode='lines',
            name=name,
            hovertemplate=hovertemplate
        )
    )

fig.update_layout(
    title=dict(text='Hourly Temperature', x=0.5),
    xaxis=dict(title='Time (Hour)', dtick=1),
    yaxis=dict(title='Temperature (°C)'),
    showlegend=True,
    height=600,
    hovermode='x'
)

# Show the plotly figure
fig.show()

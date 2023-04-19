import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

filename = "Trend-2021-09-09_08-02_30.csv"

# Read the CSV file and select columns
fields = ["Arbeit [MWh]", "Außentemperatur [°C]", "Zeit"]
df = pd.read_csv(filename, delimiter=";", usecols=fields)

# Rename columns
df.rename(columns={'Arbeit [MWh]': 'Arbeit', 'Außentemperatur [°C]': 'Außentemperatur'}, inplace=True)

# Convert columns to appropriate data types
df['Arbeit'] = df['Arbeit'].str.replace(',', '.').astype(float)
df['Außentemperatur'] = df['Außentemperatur'].str.replace(',', '.').astype(float)
df['Zeit'] = pd.to_datetime(df['Zeit'], format='%d.%m.%Y %H:%M:%S')

# Filter Arbeit > 0
df = df[df['Arbeit'] > 0]

# Set the index of the DataFrame to the "Zeit" column
df.set_index('Zeit', inplace=True)

# ----- Process Temperature, Energy Data -----
# Group the DataFrame by the month and calculate the mean of 'Außentemperatur'
monthly_temp = df['Außentemperatur'].groupby(pd.Grouper(freq='M')).mean()

# Group the DataFrame by the month and calculate the monthly total 'Arbeit'
monthly_energy = df['Arbeit'].groupby(pd.Grouper(freq='M')).max().diff().fillna(method='bfill')

# ----- Temperature, Energy Chart -----
# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
temp_trace = go.Scatter(x=monthly_temp.index, y=monthly_temp, mode='lines', name='Average Temperature',
                        hovertemplate='%{y:.1f}°C<extra></extra>')
energy_trace = go.Scatter(x=monthly_energy.index, y=monthly_energy, mode='lines', name='Energy',
                          hovertemplate='%{y:.2f} MWh<extra></extra>')
fig.add_trace(temp_trace, secondary_y=False)
fig.add_trace(energy_trace, secondary_y=True)

# Update layout
fig.update_layout(
    title=dict(text="Monthly Average Temperature and Total Energy", x=0.5),
    showlegend=False,
    height=600,
    hovermode="x"
)

# Set x-axis title
fig.update_xaxes(title_text="Month", tickangle=-90, tickformat='%m.%Y', showticklabels=True, dtick='M1')

# Set y-axes titles
fig.update_yaxes(title_text="<b>Average Temperature (°C)</b>", secondary_y=False, showgrid=True, title_font=dict(color='blue'), dtick=2.5)
fig.update_yaxes(title_text="<b>Energy (MWh)</b>", secondary_y=True, showgrid=False, title_font=dict(color='red'))

# Remove trace name from hover box
fig.update_traces(showlegend=False)

# Show the plotly figure
fig.show()

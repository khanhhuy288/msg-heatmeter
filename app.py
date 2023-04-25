import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime

import holidays
import streamlit as st

FILENAME = "Trend-2021-09-09_08-02_30.csv"
THEME = None

st.set_page_config(page_title="Heat Meter Dashboard",
                   page_icon=":timer_clock:",
                   layout='wide')

# Read the CSV file and select columns
fields = ["Leistung [kW]", "Zeit", "Arbeit [MWh]",
          "Außentemperatur [°C]",
          "Prim. Vorlauf [°C]",
          "Prim. Rücklauf [°C]", "Rücklauf 1 [°C]", "Rücklauf 2 [°C]", "Vorlauf 1 [°C]"]


@st.cache_data
def load_data(filename, fields):
    return pd.read_csv(filename, delimiter=";", usecols=fields)


df = load_data(FILENAME, fields)

# Rename columns
df.rename(columns={'Leistung [kW]': 'Leistung', "Arbeit [MWh]": "Arbeit",
                   'Außentemperatur [°C]': 'Außentemperatur',
                   "Prim. Vorlauf [°C]": "Prim. Vorlauf",
                   "Prim. Rücklauf [°C]": "Prim. Rücklauf",
                   "Rücklauf 1 [°C]": "Rücklauf 1",
                   "Rücklauf 2 [°C]": "Rücklauf 2",
                   "Vorlauf 1 [°C]": "Vorlauf 1"}, inplace=True)

# Convert columns to appropriate data types
df['Leistung'] = df['Leistung'].str.replace(',', '.').astype(float)
df['Arbeit'] = df['Arbeit'].str.replace(',', '.').astype(float)
df['Zeit'] = pd.to_datetime(df['Zeit'], format='%d.%m.%Y %H:%M:%S')

df['Außentemperatur'] = df['Außentemperatur'].str.replace(',', '.').astype(float)

df['Rücklauf 1'] = df['Rücklauf 1'].str.replace(',', '.').astype(float)
df['Rücklauf 2'] = df['Rücklauf 2'].str.replace(',', '.').astype(float)
df['Vorlauf 1'] = df['Vorlauf 1'].str.replace(',', '.').astype(float)

# Filter Arbeit > 0
df = df[df['Arbeit'] > 0]

# Set the index of the DataFrame to the "Zeit" column
df.set_index('Zeit', inplace=True)

# Sidebar
st.sidebar.header("Please filter here:")

# Create a date range selector
selected_date_range = st.sidebar.slider(
    "Select date range:",
    min_value=df.index.min().date(),
    max_value=df.index.max().date(),
    value=(df.index.min().date(), df.index.max().date()),
    format="DD.MM.YY"
)

# Create a checkbox for heating season
is_heating_season = st.sidebar.checkbox("Heating season only (01.10 - 30.04)")

# Filter the DataFrame based on the selected date range and the heating season checkbox
df = df.loc[(df.index.date >= selected_date_range[0])
            & (df.index.date <= selected_date_range[1])]
if is_heating_season:
    df = df.loc[(df.index.month >= 10) | (df.index.month <= 4)]

# ----- Process Load Profile Data -----
# Create a holiday mask
bayern_holidays = holidays.country_holidays('DE', subdiv='BY', years=df.index.year.unique())
holiday_mask = [date in bayern_holidays for date in df.index.date]

# Create a DataFrame with the mean hourly load for different types of days
df_weekday = df[df.index.weekday < 5]
df_saturday = df[df.index.weekday == 5]
df_sunday = df[df.index.weekday == 6]
df_holiday = df[holiday_mask]

weekday_load = df_weekday['Leistung'].groupby(df_weekday.index.hour).mean()
saturday_load = df_saturday['Leistung'].groupby(df_saturday.index.hour).mean()
sunday_load = df_sunday['Leistung'].groupby(df_sunday.index.hour).mean()
holiday_load = df_holiday['Leistung'].groupby(df_holiday.index.hour).mean()

# ----- Process Temperature, Energy Data -----
# Group the DataFrame by the month and calculate the mean of 'Außentemperatur'
monthly_temp = df['Außentemperatur'].groupby(pd.Grouper(freq='M')).mean()
monthly_temp.index = monthly_temp.index - pd.offsets.MonthBegin(1)

# Group the DataFrame by the month and calculate the monthly total 'Arbeit'
monthly_energy = df['Arbeit'].groupby(pd.Grouper(freq='M')).max().diff().fillna(method='bfill', limit=1)
monthly_energy.index = monthly_energy.index - pd.offsets.MonthBegin(1)

# ----- Process Temperature Data -----
# Calculate mean temperature for each hour
temps = df.groupby(df.index.hour).mean()
temp_cols = ['Prim. Vorlauf', 'Prim. Rücklauf',
             'Außentemperatur', 'Rücklauf 1', 'Rücklauf 2', 'Vorlauf 1']
temp_data = [(temps[col], col) for col in temp_cols]

# ----- Load Profile Chart -----
# Define the data and layout
hour_values = list(range(0, 24))
hovertemplate = '%{y:.2f} kW'
load_data = [(weekday_load, 'Weekdays'),
             (saturday_load, 'Saturdays'),
             (sunday_load, 'Sundays'),
             (holiday_load, 'Holidays')]

load_fig = go.Figure()

for load, name in load_data:
    load_fig.add_trace(
        go.Scatter(
            x=hour_values,
            y=load,
            mode='lines',
            name=name,
            hovertemplate=hovertemplate
        )
    )

load_fig.update_layout(
    title=dict(text='Load Profile'),
    xaxis=dict(title='Time (Hour)', dtick=1),
    yaxis=dict(title='Load (kW)'),
    hovermode='x'
)

# ----- Temperature, Energy Chart -----
# Create figure with secondary y-axis
temp_energy_fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
temp_trace = go.Scatter(x=monthly_temp.index, y=monthly_temp, mode='lines', name='Average Temperature',
                        hovertemplate='%{y:.1f}°C<extra></extra>')
energy_trace = go.Scatter(x=monthly_energy.index, y=monthly_energy, mode='lines', name='Energy',
                          hovertemplate='%{y:.2f} MWh<extra></extra>')
temp_energy_fig.add_trace(temp_trace, secondary_y=False)
temp_energy_fig.add_trace(energy_trace, secondary_y=True)

# Update layout
temp_energy_fig.update_layout(
    title=dict(text="Monthly Average Temperature and Total Energy"),
    showlegend=False,
    hovermode="x"
)

# Set x-axis title
temp_energy_fig.update_xaxes(title_text="Month", tickangle=-90, tickformat='%m.%Y', showticklabels=True, dtick='M1')

# Set y-axes titles
temp_energy_fig.update_yaxes(title_text="Average Temperature (°C)", secondary_y=False, showgrid=True,
                             title_font=dict(color='blue'), dtick=2.5)
temp_energy_fig.update_yaxes(title_text="Energy (MWh)", secondary_y=True, showgrid=False, title_font=dict(color='red'))

# Remove trace name from hover box
temp_energy_fig.update_traces(showlegend=False)

# ----- Temperature Chart -----
# Define the traces for each line
hour_values = list(range(0, 24))
hovertemplate = '%{y:.1f}°C'

temp_fig = go.Figure()

for temp, name in temp_data:
    temp_fig.add_trace(
        go.Scatter(
            x=hour_values,
            y=temp,
            mode='lines',
            name=name,
            hovertemplate=hovertemplate
        )
    )

temp_fig.update_layout(
    title=dict(text='Hourly Temperature'),
    xaxis=dict(title='Time (Hour)', dtick=1),
    yaxis=dict(title='Temperature (°C)'),
    showlegend=True,
    hovermode='x'
)

# Main Page
st.title(":timer_clock: Heat Meter Dashboard")

st.plotly_chart(load_fig, theme=THEME)
st.plotly_chart(temp_energy_fig, theme=THEME)
st.plotly_chart(temp_fig, theme=THEME)

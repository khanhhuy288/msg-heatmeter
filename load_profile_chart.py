import pandas as pd
import plotly.graph_objs as go
import holidays

filename = "Trend-2021-09-09_08-02_30.csv"

# Read the CSV file and select columns
fields = ["Leistung [kW]", "Zeit", "Arbeit [MWh]"]
df = pd.read_csv(filename, delimiter=";", usecols=fields)

# Rename columns
df.rename(columns={'Leistung [kW]': 'Leistung', "Arbeit [MWh]": "Arbeit"}, inplace=True)

# Convert columns to appropriate data types
df['Leistung'] = df['Leistung'].str.replace(',', '.').astype(float)
df['Arbeit'] = df['Arbeit'].str.replace(',', '.').astype(float)
df['Zeit'] = pd.to_datetime(df['Zeit'], format='%d.%m.%Y %H:%M:%S')

# Filter Arbeit > 0
df = df[df['Arbeit'] > 0]

# Set the index of the DataFrame to the "Zeit" column
df.set_index('Zeit', inplace=True)

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

# ----- Load Profile Chart -----
# Define the data and layout
hour_values = list(range(0, 24))
load_data = [(weekday_load, 'Weekdays'),
             (saturday_load, 'Saturdays'),
             (sunday_load, 'Sundays'),
             (holiday_load, 'Holidays')]

fig = go.Figure()

for load, name in load_data:
    fig.add_trace(
        go.Scatter(
            x=hour_values,
            y=load,
            mode='lines',
            name=name,
            hovertemplate='%{y:.2f} kW'
        )
    )

fig.update_layout(
    title=dict(text='Load Profile', x=0.5),
    xaxis=dict(title='Time (Hour)', dtick=1),
    yaxis=dict(title='Load (kW)'),
    legend=dict(x=0.85, y=0.95, traceorder='normal'),
    height=600,
    hovermode='x'
)

# Show the plotly figure
fig.show()



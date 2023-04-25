import streamlit as st
from data_processing import load_data, filter_data, process_load_profile_data, \
    process_temperature_energy_data, process_temperature_data
from charts import create_load_profile_chart, create_temperature_energy_chart, create_temperature_chart
from sidebar import create_sidebar

FILENAME = "Trend-2021-09-09_08-02_30.csv"
THEME = None
FIELDS = ["Leistung [kW]", "Zeit", "Arbeit [MWh]",
          "Außentemperatur [°C]", "Prim. Vorlauf [°C]",
          "Prim. Rücklauf [°C]", "Rücklauf 1 [°C]",
          "Rücklauf 2 [°C]", "Vorlauf 1 [°C]"]

st.set_page_config(page_title="Heat Meter Dashboard",
                   page_icon=":timer_clock:",
                   layout='wide')

# Main Page
st.title(":timer_clock: Heat Meter Dashboard")
st.markdown("---")

df = load_data(FILENAME, FIELDS)
selected_date_range, is_heating_season = create_sidebar(df)

df = filter_data(df, selected_date_range, is_heating_season)
load_data = process_load_profile_data(df)
monthly_temp, monthly_energy = process_temperature_energy_data(df)
temp_data = process_temperature_data(df)

load_fig = create_load_profile_chart(load_data)
temp_energy_fig = create_temperature_energy_chart(monthly_temp, monthly_energy)
temp_fig = create_temperature_chart(temp_data)

st.plotly_chart(load_fig, theme=THEME)
st.plotly_chart(temp_energy_fig, theme=THEME)
st.plotly_chart(temp_fig, theme=THEME)

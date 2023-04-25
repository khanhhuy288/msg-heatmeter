import streamlit as st


def create_sidebar(df):
    st.sidebar.header("Hier filtern:")

    # Create a date range selector
    selected_date_range = st.sidebar.slider(
        "Datumsbereich wählen:",
        min_value=df.index.min().date(),
        max_value=df.index.max().date(),
        value=(df.index.min().date(), df.index.max().date()),
        format="DD.MM.YY"
    )

    # Create a checkbox for heating season
    is_heating_season = st.sidebar.checkbox("Nur Heizperiode (01.10 - 30.04)")

    return selected_date_range, is_heating_season

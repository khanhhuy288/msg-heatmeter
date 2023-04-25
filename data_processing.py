import pandas as pd
import holidays
import streamlit as st


@st.cache_data
def load_data(filename, fields):
    # Read the CSV file and select columns
    df = pd.read_csv(filename, delimiter=";", usecols=fields)

    # Rename columns
    df.rename(columns={'Leistung [kW]': 'Leistung', "Arbeit [MWh]": "Arbeit",
                       'Außentemperatur [°C]': 'Außentemperatur',
                       "Prim. Vorlauf [°C]": "Prim. Vorlauf",
                       "Prim. Rücklauf [°C]": "Prim. Rücklauf",
                       "Rücklauf 1 [°C]": "Rücklauf 1",
                       "Rücklauf 2 [°C]": "Rücklauf 2",
                       "Vorlauf 1 [°C]": "Vorlauf 1"}, inplace=True)

    # Convert columns to appropriate data types
    df['Zeit'] = pd.to_datetime(df['Zeit'], format='%d.%m.%Y %H:%M:%S')
    df[['Leistung', 'Arbeit', 'Außentemperatur', 'Rücklauf 1', 'Rücklauf 2', 'Vorlauf 1']] = \
        df[['Leistung', 'Arbeit', 'Außentemperatur', 'Rücklauf 1', 'Rücklauf 2', 'Vorlauf 1']].applymap(
            lambda x: float(x.replace(',', '.')))

    # Filter Arbeit > 0
    df = df[df['Arbeit'] > 0]

    # Set the index of the DataFrame to the "Zeit" column
    df.set_index('Zeit', inplace=True)

    return df


def filter_data(df, selected_date_range, is_heating_season):
    df = df.loc[(df.index.date >= selected_date_range[0])
                & (df.index.date <= selected_date_range[1])]

    if is_heating_season:
        df = df.loc[(df.index.month >= 10) | (df.index.month <= 4)]

    return df


def process_load_profile_data(df):
    # ----- Process Load Profile Data -----
    bayern_holidays = holidays.country_holidays('DE', subdiv='BY', years=df.index.year.unique())
    holiday_mask = [date in bayern_holidays for date in df.index.date]

    df_weekday = df[df.index.weekday < 5]
    df_saturday = df[df.index.weekday == 5]
    df_sunday = df[df.index.weekday == 6]
    df_holiday = df[holiday_mask]

    load_profile_data = {
        'Weekdays': df_weekday['Leistung'].groupby(df_weekday.index.hour).mean(),
        'Saturdays': df_saturday['Leistung'].groupby(df_saturday.index.hour).mean(),
        'Sundays': df_sunday['Leistung'].groupby(df_sunday.index.hour).mean(),
        'Holidays': df_holiday['Leistung'].groupby(df_holiday.index.hour).mean()
    }

    return load_profile_data


def process_temperature_energy_data(df):
    monthly_temp = df['Außentemperatur'].groupby(pd.Grouper(freq='M')).mean()
    monthly_temp.index = monthly_temp.index - pd.offsets.MonthBegin(1)

    monthly_energy = df['Arbeit'].groupby(pd.Grouper(freq='M')).max().diff().fillna(method='bfill', limit=1)
    monthly_energy.index = monthly_energy.index - pd.offsets.MonthBegin(1)

    return monthly_temp, monthly_energy


def process_temperature_data(df):
    # ----- Process Temperature Data -----
    temps = df.groupby(df.index.hour).mean()
    temp_cols = ['Prim. Vorlauf', 'Prim. Rücklauf', 'Außentemperatur', 'Rücklauf 1', 'Rücklauf 2', 'Vorlauf 1']
    temp_data = {col: temps[col] for col in temp_cols}

    return temp_data

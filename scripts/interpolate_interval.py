import pandas as pd
import altair as alt
import streamlit as st
import pyield as pyd
from pyield.interpolator import Interpolator

def interpolate_rates_for_dates(df, days_to_expiration, start_date, end_date):
    # Convert the date strings to pandas datetime objects for comparison
    df['Date'] = pd.to_datetime(df['Date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the DataFrame for the date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # Get unique reference dates within the filtered DataFrame
    unique_reference_dates = filtered_df['Date'].unique()

    # Prepare the output list
    dates = []
    interpolations = []

    # Loop through each unique reference date
    for ref_date in unique_reference_dates:
        # Filter the DataFrame for the current reference date
        ref_date_df = filtered_df[filtered_df['Date'] == ref_date]

        # Initialize the Interpolator with the known days and rates
        known_bdays = ref_date_df['bdays'].tolist()
        known_rates = ref_date_df['premio_taxa'].tolist() 
        interpolator = Interpolator("flat_forward", known_bdays, known_rates)

        # Interpolate the rate for the given days_to_expiration
        try:
            interpolated_rate = round(interpolator(days_to_expiration * 252),6)
            interpolations.append(interpolated_rate)
            dates.append(ref_date.strftime("%Y-%m-%d"))
        except:
            pass

    return interpolations, dates


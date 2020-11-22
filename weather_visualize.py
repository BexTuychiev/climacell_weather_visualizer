# Streamlit framework
import streamlit as st
# Scientific libs
import numpy as np
import pandas as pd
# Base libs
import time
from datetime import datetime, timedelta
from PIL import Image
import os
import json
# String matching
from fuzzywuzzy import process
# API, web
import requests


def main():
    run_app()


def run_app():
    """
    A function to run
    the main part of the program
    """

    @st.cache
    def load_data(path):
        """
        A function load data
        :param path: a path to the file source
        :return: pandas.DataFrame instance
        """
        df = pd.read_csv(path)
        return df

    @st.cache
    def match_country(custom_input, df):
        """
        Match user input to available
        countries in the
        :param custom_input: text input for country
        :param df: main data
        :return: matching country as str
        """
        # Store unique country names
        unique_countries = set(df['country'].unique())
        # Find all matches for user_input
        match = process.extractOne(custom_input, unique_countries)
        # If similarity is over 70
        if match[1] >= 80:
            return match[0]
        else:
            return 'No match'

    @st.cache
    def top25(df, country):
        """
        Subset for the top <25
        cities of the given country
        :param df: a dataset containing coords
                   for cities and countries
        :param country: a country matched from
                        user input
        :return: pandas.DataFrame containing
                 coords for top 25 cities
                 of given country
        """
        # Subset for cities of given country
        subset = df[df['country'] == country][['city_ascii', 'lat',
                                               'lng', 'population']]
        # Extract top 25 based on population size
        subset_sorted = subset.sort_values('population',
                                           ascending=False).iloc[:25]
        # Rename lng column to lon
        subset_sorted['lon'] = subset_sorted['lng']
        # Drop lng column
        subset_sorted.drop('lng', axis='columns', inplace=True)
        # Reorder columns
        subset_sorted = subset_sorted[['city_ascii', 'lat',
                                       'lon', 'population']]
        return subset_sorted.reset_index().drop('index', axis='columns')

    def call_api(cities_df):
        """
        Get current weather data
        for top25 cities from cities_df
        based on lat/lon
        :param cities_df: pandas.DataFrame with cities sorted by pop
        :return:
        """
        # Realtime endpoint
        weather_endpoint = "https://api.climacell.co/v3/weather/realtime"
        # Query params
        params = {
            'unit_system': 'si',  # TODO change unit system to dynamic
            'fields': 'temp',
            'apikey': os.environ['CLIMACELL_API'], # TODO dynamic api input
            'lat': '',
            'lon': ''
        }
        # Get time for the moment
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        def call(row):
            """
            Function to return realtime temperature
            for each lat, lon
            """
            # Build querystring params
            params['lat'] = str(row['lat'])
            params['lon'] = str(row['lon'])
            # Make an API call
            response = requests.request("GET", weather_endpoint, params=params)
            response = json.loads(response.content)
            # Update row
            return response['temp']['value']
        # Call for API for each row
        cities_df[f'temp({now})'] = cities_df.apply(call, axis=1)
        return cities_df

    # Load cities data with locations
    cities = load_data('data/worldcities.csv')

    # Set a title
    st.title('Visualize Weather Patterns')
    # Create radio options for location input
    st.subheader('Choose the option to input location:')
    action = st.radio('',
                      ['Custom Country Input', 'Choose From Dropdown'])

    # Depending on action
    if action == 'Custom Country Input':
        user_input = st.text_input('Enter country (basic string matching '
                                   'is enabled under the hood):', max_chars=60)
        if user_input:
            with st.spinner('Matching the closest country name'):
                # Match the input to existing countries
                country_input = match_country(user_input, cities)
                if country_input != 'No match':
                    st.markdown(f"Matched **{country_input}**")
                    st.dataframe(top25(cities, country_input))
                    # TODO
                else:
                    st.error('Could not find a match from the database. Try again...')
    else:
        # Create a dropdown
        country_input = st.selectbox('Choose your country',
                                     sorted([''] + list(cities['country'].unique())))
        if country_input:
            st.markdown(f"You chose **{country_input}**")
            top_cities = top25(cities, country_input)
            st.dataframe(call_api(cities_df=top_cities))
            # TODO


if __name__ == '__main__':
    main()

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
# Visualization
import plotly.express as px

# Set Mapbox Token
px.set_mapbox_access_token(
    'pk.eyJ1IjoiaWJleG9yaWdpbiIsImEiOiJja2h0Mjc3ZHc'
    'wNmp3MnNwNTloYTJsbHpwIn0.uXZfhBAuZ5IrutGIRMwDsw')


# Wrapper function around the main functions with behind logic
def main():
    # Create a dropdown for app mode
    st.sidebar.markdown("""
        <h2>Choose the mode:</h2>    
    """, unsafe_allow_html=True)
    mode = st.sidebar.selectbox('', [
        'Instructions and code explanation',
        'Run the app',
        'Source code'
    ])
    # Create an input field for user's API
    api = st.sidebar.text_input('Please enter your Climacell API:', max_chars=32,
                                type='password')
    api_placeholder = st.sidebar.markdown("<small>If you don't have one, get it "
                                          "[here](https://developer.climacell.co/sign-up). It is free."
                                          "</small>",
                                          unsafe_allow_html=True)

    # not_valid = True
    # while not_valid:
    #     if api:  # If api is given, empty the instructions
    #         print(api)
    #         api_placeholder.empty()
    #         with st.spinner('Validating your API key, little patience...'):
    #             if validate_api(api):
    #                 not_valid = False
    #                 st.success('Your key is valid! Choose the \'Run app\' mode to get started')
    #             else:
    #                 st.error('Validation failed! Please provide a valid API key...')
    if mode == 'Instructions and code explanation':
        pass
    elif mode == 'Run the app':
        run_app(api)
    else:
        pass  # TODO create a function to show source code


def validate_api(api):
    """
    Validates the API key by sending
    a single request to Climacell API
    :param api: 32-char API ket
    :return: True if api is valid
    """
    endpoint = "https://api.climacell.co/v3/weather/realtime"
    # Build sample params
    params = {'lat': '0', 'lon': '0', 'fields': 'temp',
              'apikey': str(api), 'unit_system': 'si'}
    # Get response
    response = requests.request('GET', endpoint, params=params)
    # If successful
    if response.status_code == 200:
        return True
    return False


def run_app(api):
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

    def call_api(cities_df, temp_unit):
        """
        Get current weather data
        for top25 cities from cities_df
        based on lat/lon
        :param temp_unit: value got from the user input radio btns
        :param cities_df: pandas.DataFrame with cities sorted by pop
        :return:
        """
        # Realtime endpoint
        weather_endpoint = "https://api.climacell.co/v3/weather/realtime"
        # Set the unit
        if temp_unit == '°C':
            temp_unit = 'si'
        else:
            temp_unit = 'us'
        # Query params
        params = {
            'unit_system': temp_unit,
            'fields': 'temp',
            'apikey': api,  # TODO dynamic api input
            'lat': '',
            'lon': ''
        }

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
            if response.status_code == 200:
                response = json.loads(response.content)
                # Update row
                return round(float(response['temp']['value']), 1)
            else:
                response = '<400>'
                return response

        # Call for API for each row
        cities_df['temperature'] = cities_df.apply(call, axis=1)
        # Create a column to resize the scatter plot dots
        cities_df['size'] = 15
        if 'population' in cities_df.columns:
            cities_df.drop('population', axis=True, inplace=True)
        # Check for status code
        if '<400>' in list(cities_df['temperature']):
            return 400, None
        else:
            return 200, cities_df

    def map_plot(df, country):
        """
        A function to plot a scatter_mapbox
        of plotly
        :param country: a country input by user
        :param df: pandas.DataFrame containing temperature
                   and cities data
        :return: plotly figure
        """
        # Change the zoom level according to the shape of df
        size = df.shape[0]
        if size == 25:
            zoom = 3
        elif size == 20:
            zoom = 4
        else:
            zoom = 5
        # Get time for the moment
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Construct the figure
        fig = px.scatter_mapbox(df, hover_data=['temperature'],
                                lat='lat', lon='lon',
                                color='temperature', size='size',
                                color_continuous_scale=px.colors.cyclical.IceFire,
                                zoom=zoom)
        fig.update_traces(textposition='top center')
        fig.update_layout(title_text=f'Temperatures for {now}, {country.title()}', title_x=0.5)

        return fig

    # Load cities data with locations
    cities = load_data('data/worldcities.csv')

    # Set a title
    st.title('Visualize Weather Patterns')
    # Create radio options for location input
    st.subheader('Choose the option to input location:')
    action = st.radio('',
                      ['Custom Country Input', 'Choose From Dropdown'])
    unit = st.radio('Choose the unit for temperature:',
                    ['°C', '°F'])
    # Depending on action
    if action == 'Custom Country Input':
        user_input = st.text_input('Enter country (basic string matching '
                                   'is enabled under the hood):', max_chars=60)
        if user_input:
            # Match the input to existing countries
            country_input = match_country(user_input, cities)
            # If country matches
            if country_input != 'No match':
                # Inform the user about their option
                st.markdown(f"Matched **{country_input}**")
                # Create waiting event while getting temp data from API
                with st.spinner('Hang on... Fetching realtime temperatures...'):
                    # Subset for top <=25 cities of the country choice
                    top_cities = top25(cities, country_input)
                    # Store results of API call
                    status, temperatures = call_api(cities_df=top_cities, temp_unit=unit)
                # If request successful
                if status == 200:
                    # Show dataframe
                    st.dataframe(temperatures.drop('size', axis=1))
                    # Create a waiting event while plotting
                    with st.spinner("Little more... Plotting the results..."):
                        # Inform the user to hover over points
                        st.subheader('Hover over the points and drag around to see temperatures')
                        # Display the plotly chart using returned data
                        st.plotly_chart(map_plot(top_cities, country_input))
                else:  # if status code != 200, it means too many requests
                    st.error('Too many requests. Please try again in an hour')
            else:  # if country_input == 'No match'
                st.error('Could not find a match from the database. Try again...')
    else:  # If user chooses to input via dropdown
        # Create a dropdown
        country_input = st.selectbox('Choose your country',
                                     sorted([''] + list(cities['country'].unique())))
        # If user choose a country from dropdown
        if country_input:
            # Inform the user about their option
            st.markdown(f"You chose **{country_input}**")
            # Create waiting event while getting temp data from API
            with st.spinner('Hang on... Fetching realtime temperatures...'):
                # Subset for top <=25 cities of the country choice
                top_cities = top25(cities, country_input)
                # Store results of API call
                status, temperatures = call_api(cities_df=top_cities, temp_unit=unit)
            # If request successful
            if status == 200:
                # Show dataframe
                st.dataframe(temperatures.drop('size', axis=1))
                # Create a waiting event while plotting
                with st.spinner("Little more... Plotting the results..."):
                    # Inform the user to hover over points
                    st.subheader('Hover over the points to see temperatures')
                    # Display the plotly chart using returned data
                    st.plotly_chart(map_plot(top_cities, country_input))
            else:  # if status code != 200, it means too many requests
                st.error('Too many requests. Please try again in an hour')


if __name__ == '__main__':
    main()

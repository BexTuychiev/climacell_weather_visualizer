import streamlit as st
import numpy as np
import pandas as pd
import time
import datetime
from PIL import Image
from fuzzywuzzy import process


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
    def match_country(user_input, df):
        """
        Match user input to available
        countries in the
        :param user_input: text input for country
        :param df: main data
        :return: matching country as str
        """
        # Store unique country names
        unique_countries = set(df['country'].unique())
        # Find all matches for user_input
        matches = process.extract(user_input, unique_countries, limit=len(unique_countries))
        result = None
        # for each match
        for m in matches:
            # If similarity higher than 85
            if m[1] >= 85:
                result = m[0]
        if result:
            return result
        else:
            st.error('Could not match any countries. Please check the input')

    # Load cities data with locations
    cities = load_data('data/worldcities.csv')

    # Set a title
    st.title('Visualize Weather Patterns')
    # Create radio options for input location
    st.subheader('Choose the option to input location:')
    action = st.radio('',
                      ['Custom Country Input', 'Choose From Dropdown'])

    # # Depending on action
    # if action == 'Custom Country Input':
    #     country_input = st.text_input('Enter country (String matching '
    #                                   'is enabled under the hood):', max_chars=60)
    #     with st.spinner('Matching the closest country name'):
    #         # Match the input to existing countries
    #         country_input = match_country(country_input)
    #


if __name__ == '__main__':
    main()

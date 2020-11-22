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



    # Load cities data with locations
    cities = load_data('data/worldcities.csv')

    # Set a title
    st.title('Visualize Weather Patterns')
    # Create radio options for input location
    st.subheader('Choose the option to input location:')
    action = st.radio('',
                      ['Custom Country Input', 'Choose From Dropdown'])

    # Depending on action
    if action == 'Custom Country Input':
        country_input = st.text_input('Enter country (String matching '
                                      'is enabled under the hood):', max_chars=60)
        with st.spinner('Matching the closest country name'):


if __name__ == '__main__':
    main()

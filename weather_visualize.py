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

    # Set a title
    st.title('Visualize Weather Patterns')
    # Create radio options for input location
    st.subheader('Choose the option to input location:')
    action = st.radio('',
                      ['Custom Country Input', 'Choose From Dropdown'])

    # Depending on action
    # if action == 'Custom Country Input':
    #     country_input = st.text_input('Enter country (String matching '
    #                                   'is enabled under the hood):', max_chars=60)
    #     with st.spinner('Matching the closest country name'):


if __name__ == '__main__':
    main()

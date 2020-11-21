import streamlit as st
import numpy as np
import pandas as pd
import time
import datetime
from PIL import Image

# Set a title to the project
st.title("Visualize Weather")
# Set a preview image
image = Image.open('images/weather.jpg')
st.image(image, caption="Photo by Quang Nguyen Vinh from Pexels", use_column_width=True)

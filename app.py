import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
from plotly.colors import qualitative

import calendar_utils

def get_color_mapping(unique_what, color_palette):
    """
    Assigns colors from the color_palette to each unique 'what'.
    If there are more 'what' items than colors, the palette repeats.
    """
    color_dict = {}
    palette_length = len(color_palette)
    for idx, item in enumerate(sorted(unique_what)):
        color_dict[item] = color_palette[idx % palette_length]
    return color_dict


st.set_page_config(layout="wide")

st.title("Training 2025")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    with st.spinner('Loading data from Google Sheets...'):
        df = conn.read()
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")
    st.stop()

df = conn.read()
df['what'] = df['what'].str.strip()

unique_what = df['what'].unique()

color_palette = qualitative.Dark24  # List of 24 colors
color_dict = get_color_mapping(unique_what, color_palette)

st.sidebar.title("Sport Type")
selected_what = []
for item in unique_what:
    if st.sidebar.checkbox(item, value=True):
        selected_what.append(item)

df['color'] = df['what'].map(color_dict)

filtered_df = df[df['what'].isin(selected_what)]

calendar_df = filtered_df.drop_duplicates(subset=['date', 'what'])
calendar_options = calendar_utils.get_options()
calendar_events = calendar_utils.generate_events(calendar_df, color_dict)
calendar_utils.display(calendar_events, calendar_options)

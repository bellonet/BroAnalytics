import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
from plotly.colors import qualitative

import calendar_utils
import plot_utils


def get_color_mapping(unique_activity, color_palette):
    """
    Assigns colors from the color_palette to each unique 'activity'.
    If there are more 'activity' items than colors, the palette repeats.
    """
    color_dict = {}
    palette_length = len(color_palette)
    for idx, item in enumerate(sorted(unique_activity)):
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

df['activity'] = df['activity'].str.strip()

unique_activity = df['activity'].unique()

color_palette = qualitative.Dark24  # List of 24 colors
color_dict = get_color_mapping(unique_activity, color_palette)
df['color'] = df['activity'].map(color_dict)

st.sidebar.title("Sport Type")
selected_activity = []

btn_col1, btn_col2 = st.sidebar.columns([1, 1])

# "Select All" Button
if btn_col1.button('Select All'):
    for activity in unique_activity:
        st.session_state[f'checkbox_{activity}'] = True
    st.rerun()

# "Select None" Button
if btn_col2.button('Select None'):
    for activity in unique_activity:
        st.session_state[f'checkbox_{activity}'] = False
    st.rerun()

# Display checkboxes for each activity
for activity in unique_activity:
    # Initialize the checkbox state if not already in session_state
    if f'checkbox_{activity}' not in st.session_state:
        st.session_state[f'checkbox_{activity}'] = True  # Default to selected

    # Render the checkbox with the current state
    if st.sidebar.checkbox(activity, value=st.session_state[f'checkbox_{activity}'], key=f'checkbox_{activity}'):
        selected_activity.append(activity)

# Filter the DataFrame based on selected activities
filtered_df = df[df['activity'].isin(selected_activity)]

calendar_df = filtered_df.drop_duplicates(subset=['date', 'activity'])
calendar_options = calendar_utils.get_options()
calendar_events = calendar_utils.generate_events(calendar_df, color_dict)
calendar_utils.display(calendar_events, calendar_options)

# Add some spacing
st.markdown("---")


st.header("Activity Counts")
activity_fig = plot_utils.plot_activity_counts(calendar_df, color_dict)
st.plotly_chart(activity_fig, use_container_width=True)

st.header("Monthly Activity Counts")
monthly_activity_fig = plot_utils.plot_monthly_activity_counts(calendar_df, color_dict)
st.plotly_chart(monthly_activity_fig, use_container_width=True)

st.header("Monthly Active Days Counts")
days_trained_fig = plot_utils.plot_days_trained_per_month(calendar_df)
st.plotly_chart(days_trained_fig, use_container_width=True)

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


st.sidebar.title("Filters")

df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

# Get the minimum and maximum dates from the DataFrame
min_date = df['date'].min().date()
max_date = df['date'].max().date()

# Add a header for the date filter section
st.sidebar.header("Date Range")


if st.sidebar.button('Reset Dates'):
    st.session_state['date_range'] = [min_date, max_date]
    st.rerun()


selected_dates = st.sidebar.date_input(
    "🗓️ Select Date Range:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date,
    key='date_range'
)

print(selected_dates)

# Validate that two dates are selected
if isinstance(selected_dates, (list, tuple)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    # Convert selected dates to pandas Timestamp for comparison
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
else:
    # Fallback to full range if not properly selected
    start_date, end_date = pd.Timestamp(min_date), pd.Timestamp(max_date)

# (Optional) Display the selected date range for user confirmation
st.sidebar.write(f"**Selected Date Range:** {start_date.date()} to {end_date.date()}")

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

filtered_df = df[
    (df['activity'].isin(selected_activity)) &
    (df['date'] >= start_date) &
    (df['date'] <= end_date)
]

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

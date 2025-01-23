import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import random


st.set_page_config(layout="wide")

st.title("Training 2025")

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read()
df['what'] = df['what'].str.strip()

unique_what = df['what'].unique()

st.sidebar.title("Sport Type")
selected_what = []
for item in unique_what:
    if st.sidebar.checkbox(item, value=True):
        selected_what.append(item)

def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

color_dict = {item: random_color() for item in unique_what}

filtered_df = df[df['what'].isin(selected_what)]

calendar_options = {
    "editable": False,
    "selectable": False,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": ""
    },
    "slotMinTime": "09:00:00",
    "slotMaxTime": "22:00:00",
    "initialView": "dayGridMonth",
}
calendar_events = [
    {
        "title": row['what'],
        "start": pd.to_datetime(row['date'], dayfirst=True).date().isoformat(),
        "end": pd.to_datetime(row['date'], dayfirst=True).date().isoformat(),
        "color": color_dict.get(row['what'], "gray")
    }
    for _, row in filtered_df.iterrows()
]
callbacks = []

calendar = calendar(events=calendar_events, options=calendar_options, callbacks=callbacks)
st.write(calendar)
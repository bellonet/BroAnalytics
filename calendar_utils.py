import pandas as pd
import streamlit as st
from streamlit_calendar import calendar


def generate_events(filtered_df, color_dict):
    """
    Generate a list of calendar events from the filtered DataFrame.
    Each 'activity' is shown only once per day.
    """
    events = []
    for _, row in filtered_df.iterrows():
        event_date = pd.to_datetime(row['date'], dayfirst=True).date().isoformat()
        event = {
            "title": row['activity'],
            "start": event_date,
            "end": event_date,
            "color": color_dict.get(row['activity'], "gray")
        }
        events.append(event)
    return events


def get_options():
    """
    Define and return the calendar configuration options.
    """
    return {
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


def display(events, options):
    """
    Display the calendar with the given events and options.
    """
    callbacks = []
    cal = calendar(events=events, options=options, callbacks=callbacks)
    st.write(cal)

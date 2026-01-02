import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Import our custom modules
from data_loader import load_data
from plots import (
    plot_overview_timeline,
    plot_activity_distribution,
    plot_monthly_volume,
    plot_monthly_reps_volume,
    plot_specific_metrics
)

##

# --- CONFIG ---
DATA_SOURCE = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRlt_GMSRudbO1-ynoxJm2G8vwW1iHkvRYwNwDr-AU-G8yqTrnxqCuQfrmcrluwjM2ujY9GGk8izkI_/pub?output=xlsx'

df_raw = load_data(DATA_SOURCE)


def get_color_map(df):
    if df.empty:
        return {}
    unique_sports = sorted(df['activity'].unique())
    color_palette = px.colors.qualitative.T10 + px.colors.qualitative.Dark24
    return {sport: color_palette[i % len(color_palette)] for i, sport in enumerate(unique_sports)}


color_map = get_color_map(df_raw)

# Initialize App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# --- STYLES ---
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# --- LAYOUT COMPONENTS ---

sidebar = html.Div(
    [
        html.H2("BroAnalytics", className="display-6"),
        html.Hr(),
        html.P("Filter your workouts", className="lead"),

        html.Label("Select Sport(s):"),
        dcc.Dropdown(id='sport-filter', multi=True, placeholder="All Sports"),
        html.Br(),

        html.Label("Date Range:"),
        dcc.DatePickerRange(id='date-filter', display_format='DD/MM/YYYY'),
        html.Br(), html.Br(),

        dbc.Button("Refresh Data", id="btn-refresh", color="primary", className="me-1"),
        html.Div(id="last-updated", className="text-muted mt-2", style={"fontSize": "0.8rem"})
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    [
        # Top Row: KPI Cards
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Days", className="card-title"),
                    html.H2(id="kpi-days", className="text-primary")
                ])
            ]), width=True),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Reps", className="card-title"),
                    html.H2(id="kpi-reps", className="text-warning")
                ])
            ]), width=True),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Volume", className="card-title", title="Sets * Reps * Weight (Tonnage)"),
                    html.H2(id="kpi-weight", className="text-danger")
                ])
            ]), width=True),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Distance", className="card-title"),
                    html.H2(id="kpi-kms", className="text-info")
                ])
            ]), width=True),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Time", className="card-title"),
                    html.H2(id="kpi-duration", className="text-success")
                ])
            ]), width=True),


        ], className="mb-4"),

        # Second Row: Session Distribution (Full Width)
        ## New: Session Distribution moved to its own full-width row
        dbc.Row([
            dbc.Col(dcc.Graph(id='pie-plot'), width=12),
        ], className="mt-4"),
        ##

        # Third Row: Activity Timeline (Full Width)
        ## New: Activity Timeline is now full-width
        dbc.Row([
            dbc.Col(dcc.Graph(id='timeline-plot'), width=12),
        ], className="mt-4"),
        ##

        # Fourth Row: Monthly Volume (Full Width)
        dbc.Row([
            dbc.Col(dcc.Graph(id='monthly-bar-plot'), width=12),
        ], className="mt-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id='monthly-reps-plot'), width=12),
        ], className="mt-4"),

        html.Hr(),
        html.H3("Deep Dive: Single Sport Analysis"),
        html.P(
            "Select a single sport in the dropdown below to see specific metrics (e.g., Volume Load, Distance vs Duration)."),

        dcc.Dropdown(
            id='single-sport-selector',
            placeholder="Select a sport for deep dive...",
            className="mb-3"
        ),

        dbc.Row([
            dbc.Col(dcc.Graph(id='specific-plot'), width=12)
        ])
    ],
    style=CONTENT_STYLE
)

app.layout = html.Div([sidebar, content])


# --- CALLBACKS ---

@app.callback(
    [Output('kpi-days', 'children'),
     Output('kpi-reps', 'children'),
     Output('kpi-weight', 'children'),
     Output('kpi-kms', 'children'),
     Output('kpi-duration', 'children'),
     Output('timeline-plot', 'figure'),
     Output('pie-plot', 'figure'),
     Output('monthly-bar-plot', 'figure'),
     Output('monthly-reps-plot', 'figure'),
     Output('specific-plot', 'figure'),
     Output('sport-filter', 'options'),
     Output('single-sport-selector', 'options'),
     Output('date-filter', 'min_date_allowed'),
     Output('date-filter', 'max_date_allowed'),
     Output('date-filter', 'start_date'),
     Output('date-filter', 'end_date')],
    [Input('sport-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('single-sport-selector', 'value'),
     Input('btn-refresh', 'n_clicks')]
)
def update_dashboard(selected_sports, start_date, end_date, deep_dive_sport, n_clicks):
    global df_raw, color_map

    ctx = dash.callback_context
    if ctx.triggered and 'btn-refresh' in ctx.triggered[0]['prop_id']:
        df_raw = load_data(CSV_SOURCE)
        color_map = get_color_map(df_raw)

    # Return empty states with correct tuple size (14 items)
    if df_raw.empty:
        return "0/0", 0, "0 t", "0 km", "0h 0m", {}, {}, {}, {}, {}, [], [], None, None, None, None

    min_date = df_raw['date_obj'].min()
    max_date = df_raw['date_obj'].max()
    current_start = start_date if start_date else min_date
    current_end = end_date if end_date else max_date

    mask = (df_raw['date_obj'] >= pd.to_datetime(current_start)) & \
           (df_raw['date_obj'] <= pd.to_datetime(current_end))
    dff = df_raw.loc[mask]

    if selected_sports:
        dff = dff[dff['activity'].isin(selected_sports)]

    start_dt = pd.to_datetime(current_start)
    end_dt = pd.to_datetime(current_end)
    total_days_range = (end_dt - start_dt).days + 1 if pd.notna(start_dt) and pd.notna(end_dt) else 0
    active_days = dff['date_obj'].dt.normalize().nunique()
    days_str = f"{active_days}/{total_days_range}" if total_days_range > 0 else "0/0"

    ## New: Total Reps Calculation
    def calc_reps(row):
        s = row['sets'] if row['sets'] > 0 else 1
        r = row['reps'] if row['reps'] > 0 else 0
        return s * r

    total_reps = int(dff.apply(calc_reps, axis=1).sum())

    ##

    ## New: Total Tonnage formatted as Tons (t)
    def calc_tonnage(row):
        s = row['sets'] if row['sets'] > 0 else 1
        r = row['reps'] if row['reps'] > 0 else 1
        w = row['weight']
        if w > 0:
            return s * r * w
        return 0

    total_kg = dff.apply(calc_tonnage, axis=1).sum()
    weight_str = f"{total_kg / 1000:.1f} t"
    ##

    total_kms = round(dff['length'].sum(), 1)
    kms_str = f"{total_kms} km"

    total_mins = dff['duration_mins'].sum()
    hours = int(total_mins // 60)
    mins = int(total_mins % 60)
    duration_str = f"{hours}h {mins}m"

    # --- Plots ---
    # Need to check if the user has renamed figures.py to plots.py
    # If the import fails at runtime, they will get an error.
    # Assuming 'plots' exists based on the request.
    fig_timeline = plot_overview_timeline(dff, color_map)
    fig_pie = plot_activity_distribution(dff, color_map)
    fig_monthly_time = plot_monthly_volume(dff, color_map)
    fig_monthly_reps = plot_monthly_reps_volume(dff, color_map)  # NEW

    dff_deep = df_raw.loc[mask]
    if deep_dive_sport:
        dff_specific = dff_deep[dff_deep['activity'] == deep_dive_sport]
        fig_specific = plot_specific_metrics(dff_specific, deep_dive_sport, color_map)  # CHANGED
    else:
        fig_specific = plot_specific_metrics(pd.DataFrame(), "None", color_map)
        fig_specific.update_layout(title="Select a sport below to see specific metrics")


    unique_sports = sorted(df_raw['activity'].unique())
    sport_options = [{'label': i.title(), 'value': i} for i in unique_sports]

    return (days_str, total_reps, weight_str, kms_str, duration_str,
            fig_timeline, fig_pie, fig_monthly_time, fig_monthly_reps, fig_specific,
            sport_options, sport_options, min_date, max_date, current_start, current_end)


if __name__ == '__main__':
    app.run(debug=True)
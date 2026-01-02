import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots

def plot_overview_timeline(df, color_map=None):
    if df.empty:
        return go.Figure()

    df = df.copy()

    activity_counts = df.groupby('activity')['date_obj'].nunique().sort_values(ascending=False)
    activity_order = activity_counts.index.tolist()

    # 1. Start with Duration. Replace 0 with NaN so we can fill it.
    df['bubble_size'] = df['duration_mins'].replace(0, np.nan)

    # 2. Create a "Length Score" (km * 5). Replace 0 with NaN here too.
    length_score = (df['length']).replace(0, np.nan)

    # 3. Fill Duration NaNs with Length Score, then fill remaining NaNs with Default (20)
    df['bubble_size'] = df['bubble_size'].fillna(length_score)
    df['bubble_size'] = df['bubble_size'].fillna(20)
    df.loc[df['bubble_size'] < 20, 'bubble_size'] = 20

    fig = px.scatter(
        df,
        x='date_obj',
        y='activity',
        size='bubble_size',
        color='activity',
        hover_data=['duration', 'length', 'comment', 'where'],
        title="Activity Timeline",
        color_discrete_map=color_map,
        # Explicitly enforce order here
        category_orders={"activity": activity_order}
    )
    fig.update_layout(
        template="plotly_white",
        yaxis_title=None,
        xaxis_title=None,
        legend=None,
        height=max(400, 30 * len(activity_order))
    )

    return fig


def plot_activity_distribution(df, color_map=None):
    if df.empty:
        return go.Figure()

    df = df.copy()
    df['day'] = df['date_obj'].dt.normalize()
    counts = df.groupby('activity')['day'].nunique().reset_index()
    counts.columns = ['activity', 'count']

    fig = px.pie(
        counts,
        values='count',
        names='activity',
        color='activity',
        hole=0.5,
        title="Session Distribution",
        color_discrete_map=color_map
    )

    texts = []
    positions = []
    for a, c in zip(counts['activity'], counts['count']):
        if c > 10:
            texts.append(f"{a} ({c})")   # outside text
            positions.append('outside')
        else:
            texts.append("")             # no text
            positions.append('outside')

    fig.update_traces(
        text=texts,
        textposition=positions,
        textinfo='text'
    )

    fig.update_layout(template="plotly_white")
    return fig



def plot_monthly_volume(df, color_map=None):
    if df.empty:
        return go.Figure()

    df['duration_hours'] = df['duration_mins'] / 60

    grouped = df.groupby(['month', 'activity'])['duration_hours'].sum().reset_index()

    activity_order = grouped.groupby('activity')['duration_hours'] \
                            .sum().sort_values(ascending=False).index.tolist()
    month_order = sorted(grouped['month'].unique())

    fig = px.bar(
        grouped,
        x='month',
        y='duration_hours',
        color='activity',
        title="Monthly Volume (Hours)",
        color_discrete_map=color_map,
        category_orders={'month': month_order, 'activity': activity_order}
    )
    fig.update_layout(
        template="plotly_white",
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title=None
        )
    )
    fig.update_xaxes(
        type='category',
        categoryorder='array',
        categoryarray=month_order,
        tickmode='array',
        tickvals=month_order,
        ticktext=month_order
    )
    return fig

def plot_monthly_reps_volume(df, color_map=None):
    if df.empty:
        return go.Figure()

    df = df.copy()

    def calc_reps(row):
        s = row['sets'] if row['sets'] > 0 else 1
        r = row['reps'] if row['reps'] > 0 else 0
        return s * r

    df['total_reps'] = df.apply(calc_reps, axis=1)
    grouped = df.groupby(['month', 'activity'])['total_reps'].sum().reset_index()

    activity_order = grouped.groupby('activity')['total_reps'] \
                            .sum().sort_values(ascending=False).index.tolist()
    month_order = sorted(grouped['month'].unique())

    fig = px.bar(
        grouped,
        x='month',
        y='total_reps',
        color='activity',
        title="Monthly Volume (Reps)",
        color_discrete_map=color_map,
        category_orders={'month': month_order, 'activity': activity_order}
    )
    fig.update_layout(
        template="plotly_white",
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title=None
        )
    )
    fig.update_xaxes(
        type='category',
        categoryorder='array',
        categoryarray=month_order,
        tickmode='array',
        tickvals=month_order,
        ticktext=month_order
    )
    fig.update_yaxes(title="Total Reps")
    return fig


def plot_specific_metrics(df, activity_name, color_map=None):
    if df.empty:
        return go.Figure().update_layout(title="No data")

    df = df.copy()
    sport_color = color_map.get(activity_name, '#636EFA') if color_map else '#636EFA'

    has_reps_sets = ((df['reps'] > 0).any() or (df['sets'] > 0).any())
    has_weight = (df['weight'] > 0).any() if 'weight' in df.columns else False
    has_time = (df['duration_mins'] > 0).any() if 'duration_mins' in df.columns else False
    has_length = (df['length'] > 0).any() if 'length' in df.columns else False

    # Time-volume sports like butterfly: time + reps/sets, but no weight/length
    has_time_volume = has_time and has_reps_sets and not has_weight and not has_length

    # Location info
    if 'where' in df.columns:
        loc_series = df['where'].dropna().astype(str).str.strip()
        loc_series = loc_series[loc_series != ""]
        has_multiple_locations = loc_series.nunique() > 1
        loc_counts = loc_series.value_counts().reset_index()
        loc_counts.columns = ['where', 'count']
    else:
        has_multiple_locations = False
        loc_counts = None

    # --- Helpers ---
    def row_reps(row):
        s = row['sets'] if row['sets'] > 0 else 1
        r = row['reps'] if row['reps'] > 0 else 0
        return s * r

    def row_weight_volume(row):
        s = row['sets'] if row['sets'] > 0 else 1
        r = row['reps'] if row['reps'] > 0 else 1
        w = row['weight']
        return s * r * w if w > 0 else 0

    def row_time_volume(row):
        s = row['sets'] if row['sets'] > 0 else 1
        r = row['reps'] if row['reps'] > 0 else 1
        return row['duration_mins'] * s * r

    # --- No reps/sets: fall back to previous distance/duration logic ---
    if not has_reps_sets:
        total_length = df['length'].sum()
        avg_duration = df['duration_mins'].mean()

        if total_length > 0:
            if avg_duration < 5:
                fig = px.bar(
                    df,
                    x='date_obj',
                    y='length',
                    title=f"{activity_name}: Distance Log",
                    hover_data=['comment', 'elevation'],
                    color_discrete_sequence=[sport_color]
                )
                fig.update_layout(template="plotly_white", yaxis_title="Distance (km)")
                return fig
            else:
                fig = px.scatter(
                    df,
                    x='duration_mins',
                    y='length',
                    size='elevation',
                    hover_data=['date_obj', 'comment'],
                    title=f"{activity_name}: Distance vs Duration",
                    color_discrete_sequence=[sport_color]
                )
                fig.update_layout(template="plotly_white")
                return fig
        else:
            fig = px.bar(
                df,
                x='date_obj',
                y='duration_mins',
                title=f"{activity_name}: Duration Log",
                hover_data=['where', 'comment'],
                color_discrete_sequence=[sport_color]
            )
            fig.update_layout(template="plotly_white", yaxis_title="Minutes")
            return fig

    # --- Reps/sets sports: deep dive with multiple subplots ---
    rows = 1
    second_metric = has_weight or has_time_volume
    if second_metric:
        rows += 1
    if has_multiple_locations:
        rows += 1

    specs = []
    for i in range(rows):
        if has_multiple_locations and i == rows - 1:
            specs.append([{"type": "domain"}])  # pie
        else:
            specs.append([{"type": "xy"}])

    subplot_titles = [f"{activity_name}<br>Total Reps x Sets per Day"]
    if has_weight:
        subplot_titles.append(f"{activity_name}<br>Total Weight per Day (kg)")
    elif has_time_volume:
        subplot_titles.append(f"{activity_name}<br>Time Volume per Day (min)")
    if has_multiple_locations:
        subplot_titles.append(f"{activity_name}<br>Sessions by Location")

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        specs=specs,
        subplot_titles=subplot_titles
    )

    # Row 1: reps x sets per day
    df['total_reps'] = df.apply(row_reps, axis=1)
    daily_reps = df.groupby('date_obj')['total_reps'].sum().reset_index()
    fig.add_trace(
        go.Bar(
            x=daily_reps['date_obj'],
            y=daily_reps['total_reps'],
            marker_color=sport_color,
            name="Reps x Sets"
        ),
        row=1,
        col=1
    )
    fig.update_yaxes(title_text="Total Reps", row=1, col=1)

    current_row = 2

    # Optional Row 2: weight or time volume per day
    if second_metric:
        if has_weight:
            df['weight_volume'] = df.apply(row_weight_volume, axis=1)
            daily_weight = df.groupby('date_obj')['weight_volume'].sum().reset_index()
            fig.add_trace(
                go.Bar(
                    x=daily_weight['date_obj'],
                    y=daily_weight['weight_volume'],
                    marker_color=sport_color,
                    name="Total Weight"
                ),
                row=current_row,
                col=1
            )
            fig.update_yaxes(title_text="Total Weight (kg)", row=current_row, col=1)
        elif has_time_volume:
            df['time_volume'] = df.apply(row_time_volume, axis=1)
            daily_time = df.groupby('date_obj')['time_volume'].sum().reset_index()
            fig.add_trace(
                go.Bar(
                    x=daily_time['date_obj'],
                    y=daily_time['time_volume'],
                    marker_color=sport_color,
                    name="Time Volume"
                ),
                row=current_row,
                col=1
            )
            fig.update_yaxes(title_text="Time Volume (min)", row=current_row, col=1)
        current_row += 1

    # Optional Row 3: location pie
    if has_multiple_locations and loc_counts is not None:
        fig.add_trace(
            go.Pie(
                labels=loc_counts['where'],
                values=loc_counts['count'],
                showlegend=False,
                name="Location"
            ),
            row=current_row,
            col=1
        )

    fig.update_layout(
        template="plotly_white",
        height=350 * rows,
        showlegend=True,
        title=f"{activity_name}: Deep Dive"
    )
    fig.update_xaxes(title_text="Date", row=rows if rows >= 1 else 1, col=1)
    return fig

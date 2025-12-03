import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def plot_overview_timeline(df, color_map=None):
    if df.empty:
        return go.Figure()

    df = df.copy()

    ## Old:
    # df['bubble_size'] = df['duration_mins'].replace(0, np.nan)
    # df['bubble_size'] = df['bubble_size'].fillna(df['length'] * 5).fillna(20)
    ##

    ## New: logic to ensure 0 length doesn't block the default fallback
    # 1. Start with Duration. Replace 0 with NaN so we can fill it.
    df['bubble_size'] = df['duration_mins'].replace(0, np.nan)

    # 2. Create a "Length Score" (km * 5). Replace 0 with NaN here too.
    length_score = (df['length']).replace(0, np.nan)

    # 3. Fill Duration NaNs with Length Score, then fill remaining NaNs with Default (20)
    df['bubble_size'] = df['bubble_size'].fillna(length_score).fillna(20)
    ##

    fig = px.scatter(
        df,
        x='date_obj',
        y='activity',
        size='bubble_size',
        color='activity',
        hover_data=['duration', 'length', 'comment', 'where'],
        title="Activity Timeline",
        color_discrete_map=color_map
    )
    fig.update_layout(
        template="plotly_white",
        yaxis_title=None,
        xaxis_title=None,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            title=None
        )
    )
    return fig


def plot_activity_distribution(df, color_map=None):
    if df.empty:
        return go.Figure()

    counts = df['activity'].value_counts().reset_index()
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

    fig.update_traces(textinfo='none')
    fig.update_layout(template="plotly_white")
    return fig


def plot_monthly_volume(df, color_map=None):
    if df.empty:
        return go.Figure()

    df['duration_hours'] = df['duration_mins'] / 60

    grouped = df.groupby(['month', 'activity'])['duration_hours'].sum().reset_index()

    fig = px.bar(
        grouped,
        x='month',
        y='duration_hours',
        color='activity',
        title="Monthly Volume (Hours)",
        color_discrete_map=color_map
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
    return fig


def plot_specific_metrics(df, activity_name, color_map=None):
    if df.empty:
        return go.Figure().update_layout(title="No data")

    sport_color = color_map.get(activity_name, '#636EFA') if color_map else None

    # Check metrics existence
    total_reps = df['reps'].sum()
    total_sets = df['sets'].sum()
    total_length = df['length'].sum()
    avg_duration = df['duration_mins'].mean()

    # 1. Gym Mode (Significant Reps/Sets)
    if total_reps > 0 or total_sets > 0:
        df['calc_weight'] = df['weight'].replace(0, 1)
        df['volume'] = df['sets'] * df['reps'] * df['calc_weight']

        fig = px.bar(
            df,
            x='date_obj',
            y='volume',
            color='weight',
            title=f"{activity_name}: Volume (Sets * Reps * Weight)",
            hover_data=['sets', 'reps', 'weight', 'comment'],
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig.update_layout(template="plotly_white", yaxis_title="Volume Load")
        return fig

    # 2. Distance Mode
    elif total_length > 0:
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

    # 3. Default: Duration Mode
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
import plotly.express as px
import pandas as pd


def plot_activity_counts(calendar_df, color_dict):
    """
    Creates a bar plot where each activity gets a bar with its count,
    counting each activity only once per day.
    """
    # Calculate counts per activity (each activity counted once per day)
    activity_counts = calendar_df['activity'].value_counts().reset_index()
    activity_counts.columns = ['activity', 'count']
    activity_counts = activity_counts.sort_values('count', ascending=False)

    # Assign colors based on activity
    activity_counts['color'] = activity_counts['activity'].map(color_dict)

    # Create the bar plot with enhanced borders
    fig = px.bar(
        activity_counts,
        x='activity',
        y='count',
        color='activity',
        color_discrete_map=color_dict,
        title='Activity Counts (Unique per Day)',
        labels={'count': 'Count', 'activity': 'Activity'},
        text='count'
    )

    # Remove legend as colors are self-explanatory
    fig.update_layout(showlegend=False)

    return fig


def plot_monthly_activity_counts(calendar_df, color_dict):
    """
    Creates a stacked bar plot where each month is a bar and all activities are counted once per day,
    with colors and enhanced borders for each activity segment.
    """
    # Ensure 'date' is in datetime format
    calendar_df['date'] = pd.to_datetime(calendar_df['date'], dayfirst=True)

    # Extract month and year for grouping
    calendar_df['month'] = calendar_df['date'].dt.to_period('M').dt.to_timestamp()

    # Group by month and activity to get counts (each activity counted once per day)
    monthly_activity = calendar_df.groupby(['month', 'activity']).size().reset_index(name='count')

    # Sort months in chronological order
    monthly_activity = monthly_activity.sort_values('month')

    # Format month for better readability
    monthly_activity['month'] = monthly_activity['month'].dt.strftime('%B %Y')

    # Create the stacked bar plot with enhanced borders
    fig = px.bar(
        monthly_activity,
        x='month',
        y='count',
        color='activity',
        color_discrete_map=color_dict,
        title='Monthly Activity Counts (Unique per Day)',
        labels={'count': 'Count', 'month': 'Month', 'activity': 'Activity'},
        text='count'
    )

    # Ensure months are in the correct order on the x-axis
    fig.update_layout(xaxis={'categoryorder': 'category ascending'})

    return fig


def plot_days_trained_per_month(calendar_df):
    """
    Creates a bar plot counting the number of unique days trained each month.

    Parameters:
    - calendar_df (pd.DataFrame): The DataFrame containing at least a 'date' column with datetime information.

    Returns:
    - fig (plotly.graph_objs._figure.Figure): The generated Plotly bar figure.
    """
    # Ensure 'date' is in datetime format
    calendar_df['date'] = pd.to_datetime(calendar_df['date'])

    # Extract month and year for grouping
    calendar_df['month'] = calendar_df['date'].dt.to_period('M').dt.to_timestamp()

    # Count unique training days per month
    monthly_days = calendar_df.groupby('month')['date'].nunique().reset_index()
    monthly_days = monthly_days.sort_values('month')

    # Format month for better readability
    monthly_days['month'] = monthly_days['month'].dt.strftime('%B %Y')

    # Create the bar plot
    fig = px.bar(
        monthly_days,
        x='month',
        y='date',
        title='Number of Days Trained Each Month',
        labels={'date': 'Number of Days Trained', 'month': 'Month'},
        text='date',
        color_discrete_sequence=["white"]  # Optional: Use a predefined color palette
    )

    # Enhance the visual appeal (optional)
    fig.update_layout(xaxis_tickangle=-45)

    return fig


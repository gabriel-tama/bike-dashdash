import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from helper import load_data, get_comparison_metrics, calculate_percentage_change

st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")




df = load_data()

st.title("🚲 Bike Rental Analysis Dashboard")

st.header("📊 Daily Report")

latest_date = df['dteday'].dt.date.max()

metrics = get_comparison_metrics(df, latest_date)

def format_change(change):
    arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
    color = "green" if change > 0 else "red" if change < 0 else "gray"
    return f"<span style='color: {color}'>{arrow} {abs(change):.1f}%</span>"

daily_col1, daily_col2, daily_col3, daily_col4 = st.columns(4)

with daily_col1:
    st.metric(
        "Today's Total Rentals",
        f"{metrics['current_total']:,}",
        delta=f"{metrics['daily_change']:,.1f}%",
        delta_color="normal"
    )

with daily_col2:
    st.markdown("### vs Yesterday")
    st.markdown(f"**{metrics['yesterday_total']:,}** ({format_change(metrics['daily_change'])})", unsafe_allow_html=True)

with daily_col3:
    st.markdown("### vs Last Week")
    st.markdown(f"**{metrics['last_week_total']:,}** ({format_change(metrics['weekly_change'])})", unsafe_allow_html=True)

with daily_col4:
    st.markdown("### vs Last Month")
    st.markdown(f"**{metrics['last_month_total']:,}** ({format_change(metrics['monthly_change'])})", unsafe_allow_html=True)

st.subheader("Last 30 Days Trend")
last_30_days = df[df['dteday'].dt.date > (latest_date - timedelta(days=30))]
daily_totals = last_30_days.groupby('dteday')['cnt'].sum().reset_index()

fig_trend = px.line(
    daily_totals,
    x='dteday',
    y='cnt',
    title="Total Rentals - Last 30 Days",
    labels={'dteday': 'Date', 'cnt': 'Total Rentals'}
)
fig_trend.update_traces(line_color='#1f77b4')
fig_trend.add_scatter(
    x=[daily_totals['dteday'].iloc[-1]],
    y=[daily_totals['cnt'].iloc[-1]],
    mode='markers',
    marker=dict(size=10, color='red'),
    name='Latest'
)
st.plotly_chart(fig_trend, use_container_width=True)

st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['dteday'].min(), df['dteday'].max()],
    min_value=df['dteday'].min(),
    max_value=df['dteday'].max()
)

season_dict = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
selected_seasons = st.sidebar.multiselect(
    "Select Seasons",
    options=list(season_dict.values()),
    default=list(season_dict.values())
)

weather_dict = {
    1: "Clear/Partly Cloudy",
    2: "Mist + Cloudy",
    3: "Light Snow/Rain",
    4: "Heavy Rain/Snow"
}
selected_weather = st.sidebar.multiselect(
    "Weather Situation",
    options=list(weather_dict.values()),
    default=list(weather_dict.values())
)
mask = (
    (df['dteday'].dt.date >= date_range[0]) &
    (df['dteday'].dt.date <= date_range[1]) &
    (df['season'].map(season_dict).isin(selected_seasons)) &
    (df['weathersit'].map(weather_dict).isin(selected_weather))
)
filtered_df = df[mask]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Total Rentals")
    total_rentals = filtered_df['cnt'].sum()
    casual_rentals = filtered_df['casual'].sum()
    registered_rentals = filtered_df['registered'].sum()
    
    col1_1, col1_2, col1_3 = st.columns(3)
    col1_1.metric("Total", f"{total_rentals:,}")
    col1_2.metric("Casual", f"{casual_rentals:,}")
    col1_3.metric("Registered", f"{registered_rentals:,}")

with col2:
    st.subheader("Average Rentals by Weather")
    weather_avg = filtered_df.groupby('weathersit')['cnt'].mean().reset_index()
    weather_avg['weathersit'] = weather_avg['weathersit'].map(weather_dict)
    
    fig_weather = px.bar(
        weather_avg,
        x='weathersit',
        y='cnt',
        title="Average Rentals by Weather Condition"
    )
    st.plotly_chart(fig_weather, use_container_width=True)

seasonal_avg = filtered_df.groupby(['season', 'mnth'])['cnt'].mean().reset_index()
seasonal_avg['season'] = seasonal_avg['season'].map(season_dict)
fig_seasonal = px.line(
    seasonal_avg,
    x='mnth',
    y='cnt',
    color='season',
    title="Average Rentals by Month and Season"
)
st.plotly_chart(fig_seasonal, use_container_width=True)

st.subheader("Temperature vs Rentals")
fig_temp = px.scatter(
    filtered_df,
    x='temp',
    y='cnt',
    color='season',
    color_discrete_map={1: 'green', 2: 'red', 3: 'orange', 4: 'blue'},
    title="Temperature vs Total Rentals",
    labels={'temp': 'Temperature (normalized)', 'cnt': 'Total Rentals'}
)
st.plotly_chart(fig_temp, use_container_width=True)

st.subheader("Additional Insights")
col3, col4 = st.columns(2)

with col3:
    weekday_avg = filtered_df.groupby('workingday')['cnt'].mean()
    fig_weekday = px.pie(
        values=weekday_avg.values,
        names=['Weekend/Holiday', 'Working Day'],
        title="Average Rentals: Working Days vs Weekends"
    )
    st.plotly_chart(fig_weekday, use_container_width=True)

with col4:
    user_dist = pd.DataFrame({
        'User Type': ['Casual', 'Registered'],
        'Count': [filtered_df['casual'].sum(), filtered_df['registered'].sum()]
    })
    fig_users = px.pie(
        user_dist,
        values='Count',
        names='User Type',
        title="User Type Distribution"
    )
    st.plotly_chart(fig_users, use_container_width=True)
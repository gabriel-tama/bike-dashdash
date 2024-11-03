import kagglehub
import streamlit as st
import pandas as pd

path = kagglehub.dataset_download("lakshmi25npathi/bike-sharing-dataset")

print("Path to dataset files:", path)
@st.cache_data
def load_data():
    df = pd.read_csv(path + "/day.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])


    return df

def calculate_percentage_change(current_value, previous_value):
    if previous_value == 0:
        return 0
    return ((current_value - previous_value) / previous_value) * 100

def get_comparison_metrics(df, current_date):
    current_date = pd.to_datetime(current_date).date()
    
    previous_day = current_date - timedelta(days=1)
    previous_week = current_date - timedelta(days=7)
    previous_month = (pd.to_datetime(current_date) - pd.DateOffset(months=1)).date()
    
    def get_daily_total(date):
        return df[df['dteday'].dt.date == date]['cnt'].sum()
    
    current_total = get_daily_total(current_date)
    yesterday_total = get_daily_total(previous_day)
    last_week_total = get_daily_total(previous_week)
    last_month_total = get_daily_total(previous_month)
    
    return {
        'current_total': current_total,
        'daily_change': calculate_percentage_change(current_total, yesterday_total),
        'weekly_change': calculate_percentage_change(current_total, last_week_total),
        'monthly_change': calculate_percentage_change(current_total, last_month_total),
        'yesterday_total': yesterday_total,
        'last_week_total': last_week_total,
        'last_month_total': last_month_total
    }

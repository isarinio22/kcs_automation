"""
Pipeline for fetching, cleaning, and preparing KCS report data.
"""

# ───────────────────────────── IMPORTS ─────────────────────────────
import pandas as pd
from datetime import datetime, timedelta
from extract.queries import fetch_ka_window, fetch_cases_window, last_n_months_window
from transform.clean import clean_articles, clean_cases
from transform.metrics import (
    close_reason_ratio,
    get_all_regions_valid_cases_and_ratios,
    median_days_to_publish,
)
from visualize.charts import (
    close_reason_overall_pie,
    close_reason_distribution_pie,
    plot_valid_cases_ratio_stacked,
)

# ───────────────────────────── DATE CALCULATIONS ─────────────────────────────
now = pd.Timestamp.now()
first_of_this_month = now.replace(day=1)
last_month_end = first_of_this_month - pd.Timedelta(days=1)
last_month_start = last_month_end.replace(day=1)
start = last_month_start.date()
end = last_month_end.date()

# ───────────────────────────── DATA FETCH & CLEAN ─────────────────────────────
df_ka = fetch_ka_window(start, end)   # DataFrame born here
df_cases = fetch_cases_window(start, end) # DataFrame born here

df_ka_clean = clean_articles(df_ka)
df_cases_clean = clean_cases(df_cases)

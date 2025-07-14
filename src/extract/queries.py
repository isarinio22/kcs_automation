import pandas as pd
from extract.snowflake_client import get_connection
from datetime import date, timedelta
from typing import Tuple

_KA_QUERY = """
SELECT *
FROM MAIN_DB.MAIN.KNOWLEDGE_ARTICLE_VERSIONS_SOURCE_T
WHERE ARTICLE_FIRST_PUBLISHED_DATE BETWEEN %(start)s AND %(end)s
"""

_CASES_QUERY = """
SELECT *
FROM MAIN_DB.MAIN.SUPPORT_CASES_T
WHERE CLOSED_DATE BETWEEN %(start)s AND %(end)s
"""



def fetch_ka_window(start: str, end: str) -> pd.DataFrame:
    with get_connection() as cn, cn.cursor() as cur:
        cur.execute(_KA_QUERY, {"start": start, "end": end})
        return cur.fetch_pandas_all()

def fetch_cases_window(start: str, end: str) -> pd.DataFrame:
    with get_connection() as cn, cn.cursor() as cur:
        cur.execute(_CASES_QUERY, {"start": start, "end": end})
        return cur.fetch_pandas_all()


def last_month_window() -> Tuple[str, str]:
    """
    Return the start-date and end-date (YYYY-MM-DD) for the
    *full* calendar month immediately preceding today.
    """
    today = date.today()
    first_this_month = today.replace(day=1)
    last_day_prev = first_this_month - timedelta(days=1)
    first_day_prev = last_day_prev.replace(day=1)
    return first_day_prev.isoformat(), last_day_prev.isoformat()

def last_n_months_window(n: int = 6):
    """
    Return the start-date and end-date (YYYY-MM-DD) for the
    *full* calendar window covering the last n months (including the current month).
    """
    today = date.today()
    # Find the first day of the current month
    first_this_month = today.replace(day=1)
    # Go back n-1 months
    month = first_this_month.month - (n - 1)
    year = first_this_month.year
    while month <= 0:
        month += 12
        year -= 1
    first_n_months_ago = first_this_month.replace(year=year, month=month)
    # End date is today
    return first_n_months_ago.isoformat(), today.isoformat()

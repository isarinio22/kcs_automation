"""
Metric calculation utilities for KCS report.
"""

import pandas as pd

CLOSE_REASONS = ['Solved by existing article', 'Solved by existing doc', 'Article Updated'
                 ,'Article Flagged', 'Article Created']
# ───────────────────────────── CLOSE REASON RATIO ─────────────────────────────

def close_reason_ratio(df_cases: pd.DataFrame, region: str | None = None):
    """
    Business rule:
        ratio =  (# rows whose close_reason is valid)
                 --------------------------------------
                 (# rows whose close_reason is NOT NULL)

    Parameters
    ----------
    region
        None      → overall float
        "ALL"     → Series for every region
        "EMEA"…   → float for that specific region
    """

    # ----------- masks -------------------------------------------------
    notna_mask = df_cases["close_reason"].notna()
    valid_mask = (
        notna_mask
        & (df_cases["close_reason"].str.strip().isin(CLOSE_REASONS))
        & (df_cases["status"].str.strip() != "Closed – Purged")
        & df_cases["owner_role"].str.contains(r"Support|Idaptive|EPM", case=False, na=False)
        & (df_cases["case_record_type"].str.strip() == "External")
        & (~df_cases["region"].str.strip().str.upper().isin(["ADMIN", "INTERNAL"]))
    )

    # ----------- helper to compute ratio from two Boolean indexers -----
    def _ratio(num_mask, denom_mask) -> float | None:
        num   = float(num_mask.sum())
        denom = float(denom_mask.sum())
        return round(num / denom, 3) if denom else None

    # ----------- overall float ----------------------------------------
    if region is None:
        return _ratio(valid_mask, notna_mask)

    # ----------- Series for every region ------------------------------
    if region.upper() == "ALL":
        regions = df_cases["region"].str.strip().str.upper()
        ratios = {}
        for reg in regions.unique():
            reg_mask = regions == reg
            ratios[reg] = _ratio(valid_mask & reg_mask, notna_mask & reg_mask)
        return pd.Series(ratios, name="close_reason_ratio")

    # ----------- single region float ----------------------------------
    reg_mask = df_cases["region"].str.strip().str.upper() == region.upper()
    return _ratio(valid_mask & reg_mask, notna_mask & reg_mask)


def close_reason_ratio_last_n_months(df_cases: pd.DataFrame, n: int = 6):
    """
    Calculate the close reason ratio for each of the last n months.

    Parameters
    ----------
    df_cases : pd.DataFrame
        DataFrame containing case data.
    n : int
        Number of months to calculate the ratio for (default is 6).

    Returns
    -------
    pd.Series
        Series with month as index and close reason ratio as values.
    """
    df_cases = df_cases.copy()
    df_cases["created_date"] = pd.to_datetime(df_cases["created_date"], utc=True)

    # Create a month column
    df_cases["month"] = df_cases["created_date"].dt.to_period("M")

    # Get the current month and calculate the start month for the last n months
    current_month = pd.Timestamp.today().to_period("M")
    start_month = current_month - (n - 1)

    # Filter for the last n months
    df_filtered = df_cases[df_cases["month"] >= start_month]

    # Calculate the close reason ratio for each month
    ratios = df_filtered.groupby("month").apply(lambda x: close_reason_ratio(x))

    return ratios.sort_index()


def close_reason_ratio_last_n_months_by_region(df_cases: pd.DataFrame, n: int = 6):
    """
    Calculate the close reason ratio for each of the last n months, for each region.

    Returns
    -------
    pd.DataFrame with columns: month, region, ratio
    """
    df_cases = df_cases.copy()
    df_cases["created_date"] = pd.to_datetime(df_cases["created_date"], utc=True)
    df_cases["month"] = df_cases["created_date"].dt.to_period("M")
    current_month = pd.Timestamp.today().to_period("M")
    start_month = current_month - (n - 1)
    df_filtered = df_cases[df_cases["month"] >= start_month]
    # Group by month and region
    grouped = df_filtered.groupby(["month", df_filtered["region"].str.strip().str.upper()])
    records = []
    for (month, region), group in grouped:
        ratio = close_reason_ratio(group)
        records.append({"month": str(month), "region": region, "ratio": ratio})
    return pd.DataFrame(records)


# ───────────────────────────── VALID CASES ─────────────────────────────

def get_valid_cases_and_ratio(df_cases: pd.DataFrame, region: str | None = None):
    """
    Returns a tuple:
    (DataFrame of all valid cases according to close_reason_ratio logic, ratio)
    If region is specified, filters for that region.
    """
    df = df_cases.copy()
    # Apply region filter if needed
    if region is not None and region.upper() != "ALL":
        df = df[df["region"].str.strip().str.upper() == region.upper()]
    notna_mask = df["close_reason"].notna()
    valid_mask = (
        notna_mask
        & (df_cases["close_reason"].str.strip().isin(CLOSE_REASONS))
        & (df["status"].str.strip() != "Closed – Purged")
        & df["owner_role"].str.contains(r"Support|Idaptive|EPM", case=False, na=False)
        & (df["case_record_type"].str.strip() == "External")
    )
    valid_cases_df = df[valid_mask].copy()
    # Compute ratio as in close_reason_ratio
    num = float(valid_mask.sum())
    denom = float(notna_mask.sum())
    ratio = round(num / denom, 3) if denom else None
    return valid_cases_df, ratio


def get_all_regions_valid_cases_and_ratios(df_cases: pd.DataFrame):
    """
    Returns a DataFrame with all regions and their valid cases and close reason ratios.
    Excludes regions 'None', None, and 'ADMIN LAND (TEST)'.
    """
    regions = df_cases["region"].str.strip().str.upper().unique()
    exclude_regions = {"NONE", None, "ADMIN LAND (TEST)"}
    records = []
    for region in regions:
        if region is None or region in exclude_regions or pd.isna(region):
            continue
        valid_cases, ratio = get_valid_cases_and_ratio(df_cases, region)
        records.append({
            "region": region,
            "valid_cases_count": len(valid_cases),
            "close_reason_ratio": ratio
        })
    return pd.DataFrame(records)


# ───────────────────────────── ARTICLE COUNTS ─────────────────────────────

def count_created_articles(df: pd.DataFrame, start, end):
    """
    Returns the count of rows where 'created_at' is in [start, end].
    Only counts articles where:
    - article_type is in ("FAQ", "How To", "Technical Issue")
    - creator_name != "BI Integration"
    Both start and end should be datetime/date objects or strings parsable by pandas.
    """
    allowed_types = {"FAQ", "How To", "Technical Issue"}
    df = df[df["article_type"].isin(allowed_types)]
    df = df[df["creator_name"] != "BI Integration"]
    df = df[df['version_is_latest'] == True]
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    if 'created_at' in df.columns:
        created_dates = pd.to_datetime(df['created_at'], errors='coerce')
        created_in_range = (created_dates >= start_dt) & (created_dates <= end_dt)
        created_count = df.loc[created_in_range].shape[0]
    else:
        created_count = 0
    return int(created_count)

def count_published_articles(df: pd.DataFrame, start, end):
    """
    Returns the count of unique article_id where 'published_at' is in [start, end] and publish_status == 'Online'.
    Only counts articles where:
    - article_type is in ("FAQ", "How to", "Technical Issue")
    - creator_name != "BI Integration"
    - version_is_latest == True
    Both start and end should be datetime/date objects or strings parsable by pandas.
    """
    allowed_types = {"FAQ", "How To", "Technical Issue"}
    df = df[df["article_type"].isin(allowed_types)]
    df = df[df["creator_name"] != "BI Integration"]
    df = df[df['version_is_latest'] == True]
    published_df = df[df["publish_status"] == "Online"]
    start_dt = pd.to_datetime(start).date()
    end_dt = pd.to_datetime(end).date()
    if 'published_at' in published_df.columns and 'article_id' in published_df.columns:
        published_dates = pd.to_datetime(published_df['published_at'], errors='coerce').dt.date
        published_in_range = (published_dates >= start_dt) & (published_dates <= end_dt)
        published_count = published_df.loc[published_in_range, 'article_id'].nunique()
    else:
        published_count = 0
    return int(published_count)


def median_days_to_publish(df: pd.DataFrame) -> float | None:
    """
    Returns the median value of 'days_to_publish', excluding nulls, for articles that are:
    - publish_status == 'Online'
    - visible_to_customers == True
    - version_is_latest == True
    - article_type in {"FAQ", "Technical Issue", "How To"}
    - published_at is not null/empty
    - internal == False
    If no valid values exist, returns None.
    """
    if "days_to_publish" not in df.columns:
        return None
    mask = (
        (df.get("publish_status") == "Online") &
        (df.get("visible_to_customers") == True) &
        (df.get("version_is_latest") == True) &
        (df.get("article_type").isin({"FAQ", "Technical Issue", "How To"})) &
        (df.get("published_at").notna()) &
        (df.get("published_at") != "") &
        (df.get("published_by_name") != "") &
        (df.get("internal") == False)
    )
    valid_days = df.loc[mask, "days_to_publish"].dropna()
    if valid_days.empty:
        return None
    return float(valid_days.median())


# ───────────────────────────── OPEN CASES ─────────────────────────────

def open_cases_week_over_week_by_region(df_cases: pd.DataFrame, end_date=None) -> pd.DataFrame:
    """
    Returns a DataFrame with the number of open cases week over week for each region,
    filtered by:
      - region != 'ADMIN LAND (TEST)' and not null
      - owner_role not in specified list
      - case_record_type != 'License'
    Optionally filters cases up to and including end_date.
    Groups weeks as: 1-7, 8-14, 15-21, 22-end of month.
    """
    # Filters
    exclude_regions = {"ADMIN LAND (TEST)", None, pd.NA, ""}
    exclude_roles = {
        "Queue – Support Mailbox",
        "Queue – Sales Ops",
        "Users Access",
        "Queue – Renewal Ops"
    }
    df = df_cases.copy()
    exclude_regions_upper = {r.upper() for r in exclude_regions if isinstance(r, str)}
    df = df[
        (~df["region"].str.strip().str.upper().isin(exclude_regions_upper))
        & (df["region"].notna())
        & (~df["owner_role"].isin(exclude_roles))
        & (df["case_record_type"] != "License")
    ]
    if end_date is not None:
        end_dt = pd.to_datetime(end_date)
        df = df[df["closed_date"] <= end_dt]
    # Add week_start column: weeks start on 1st, 8th, 15th, 22nd. All days after 22nd are grouped as 22nd.
    def get_month_week_start(dt):
        day = dt.day
        if day <= 7:
            return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif day <= 14:
            return dt.replace(day=8, hour=0, minute=0, second=0, microsecond=0)
        elif day <= 21:
            return dt.replace(day=15, hour=0, minute=0, second=0, microsecond=0)
        else:
            return dt.replace(day=22, hour=0, minute=0, second=0, microsecond=0)
    df["week_start"] = pd.to_datetime(df["closed_date"]).apply(get_month_week_start)
    df["week_start"] = pd.to_datetime(df["week_start"]).dt.normalize()
    # Group and count
    result = (
        df.groupby(["week_start", df["region"].str.strip().str.upper()])
        .size()
        .reset_index(name="open_cases_count")
    )
    # Always rename columns to 'week' and 'REGION' for downstream compatibility
    result = result.rename(columns={"region": "REGION", "week_start": "week"})
    return result


# ───────────────────────────── OSP KCS ENGAGEMENT ─────────────────────────────

def osp_kcs_engagement(df_cases: pd.DataFrame) -> dict:
    """
    Calculate OSP_KCS Engagement for the last full calendar month.
    Filters:
      - case_record_type == 'External'
      - owner_role contains 'Idaptive' or 'Support' (case-insensitive)
      - status != 'Closed – Purged'
      - owner_company in ('Solugenix', 'Helpware')
      - created_date within the last full calendar month
    Returns:
      - dict with filtered DataFrame, count, close_reason ratio, and denominator
    """
    import pandas as pd

    today = pd.Timestamp.today()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - pd.Timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    mask = (
        (df_cases["case_record_type"].str.strip() == "External") &
        (df_cases["owner_role"].str.contains(r"Idaptive|Support", case=False, na=False)) &
        (df_cases["status"].str.strip() != "Closed – Purged") &
        (df_cases["owner_company"].isin(["Solugenix", "Helpware"])) &
        (df_cases["created_date"] >= last_month_start) &
        (df_cases["created_date"] <= last_month_end)
    )
    filtered = df_cases[mask].copy()
    count = len(filtered)
    notna_mask = filtered["close_reason"].notna()
    valid_mask = notna_mask & (filtered["close_reason"].str.casefold().isin(CLOSE_REASONS))
    denom = notna_mask.sum()
    num = valid_mask.sum()
    ratio = float(num) / float(denom) if denom else None
    if ratio is not None:
        ratio = round(ratio, 3)
    result = {
        "filtered_df": filtered,
        "count": count,
        "close_reason_ratio": ratio,
        "close_reason_denom": int(denom)
    }
    return result

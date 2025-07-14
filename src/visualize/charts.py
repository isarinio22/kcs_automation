"""
Visualization functions for KCS report charts.
"""

# ── src/visualize/charts.py ──────────────────────────────────────────
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from transform.metrics import (
    close_reason_ratio,
    close_reason_ratio_last_n_months,
)

CLOSE_REASONS = ['Solved by existing article', 'Solved by existing doc', 'Article Updated'
                 ,'Article Flagged', 'Article Created']

# ───────────────────────────── PIE CHARTS ─────────────────────────────


def close_reason_overall_pie(df_cases: pd.DataFrame):
    """
    Donut chart showing the overall share of cases whose close_reason
    is meaningful (NOT NULL / NOT 'Not Applicable').
    Now also displays the actual counts in addition to the ratio.

    Returns
    -------
    Tuple[plotly.graph_objs.Figure, str]
        (figure, insight_string)
    """
    # Apply additional filters as requested
    df_cases = df_cases[
        (df_cases["close_reason"].notnull()) &
        (df_cases["case_record_type"].str.strip() == "External") &
        (df_cases["owner_role"].str.contains(r"Idaptive|Support|support|EPM", case=False, na=False)) &
        (df_cases["status"].str.strip() != "Closed – Purged")
    ]
    # Calculate valid and non-actionable counts
    total_count = len(df_cases)
    valid_mask = (df_cases["close_reason"].str.strip().isin(CLOSE_REASONS))
    valid_count = valid_mask.sum()
    non_actionable_count = total_count - valid_count
    professional_colors = ["#2E86AB", "#B0B7BC"]  # Blue, Gray
    fig = px.pie(
        names=["KCS ACTION TAKEN", "NON-ACTIONABLE"],
        values=[valid_count, non_actionable_count],
        hole=0.4,
        title="Overall Close-Reason Quality",
        color_discrete_sequence=professional_colors,
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{percent:.1%}<br>%{value} cases"
    )
    fig.update_layout(showlegend=False, margin=dict(t=60, b=20, l=20, r=20))
    # Compose insight string
    if total_count > 0:
        percent = valid_count / total_count * 100
        insight = f"{percent:.1f}"
    else:
        insight = "No data available for KCS Engagement insight."
    return fig, insight


def close_reason_distribution_pie(df_cases: pd.DataFrame, title: str = "Close Reason Distribution"):
    """
    Create a styled donut chart showing the distribution of close_reason values.
    Excludes null/empty values and groups rare values as 'Other'.
    """
    # Apply additional filters as requested
    df_cases = df_cases[
        (df_cases["case_record_type"].str.strip() == "External") &
        (df_cases["owner_role"].str.contains(r"Idaptive|Support|EPM", case=False, na=False)) &
        (df_cases["status"].str.strip() != "Closed – Purged")
    ]
    # Clean and filter close_reason
    close_reason = df_cases["close_reason"].fillna("(Missing)").str.strip()
    # Exclude '(Missing)' from the analysis
    close_reason = close_reason[close_reason != "(Missing)"]
    value_counts = close_reason.value_counts()
    # Group rare values as 'Other' (less than 3% of total)
    total = value_counts.sum()
    threshold = total * 0.03
    main_reasons = value_counts[value_counts >= threshold]
    other_reasons = value_counts[value_counts < threshold]
    pie_data = main_reasons.copy()
    if not other_reasons.empty:
        pie_data["Other"] = other_reasons.sum()
    pie_data = pie_data.reset_index()
    pie_data.columns = ["close_reason", "count"]
    fig = px.pie(
        pie_data,
        names="close_reason",
        values="count",
        hole=0.5,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label+value",  # Add value to the donut parts
        textfont_size=14,
        pull=[0.05 if v == pie_data["count"].max() else 0 for v in pie_data["count"]],
    )
    fig.update_layout(
        showlegend=True,
        legend_title_text="Close Reason",
        margin=dict(t=60, b=20, l=20, r=20),
        font=dict(family="Arial", size=14),
        title_x=0.5,
    )
    return fig


# ───────────────────────────── BAR CHARTS ─────────────────────────────


def plot_valid_cases_ratio_stacked(
    df: pd.DataFrame,
    region_col: str = "region",
    count_col: str = "valid_cases_count",
    ratio_col: str = "close_reason_ratio",
    *,
    title: str = "Valid-Cases Breakdown by Region",
    figsize: tuple = (9, 5),
    small_frac: float = 0.06,   # move upper label outside if segment < 6 % of total range
    apply_metrics: bool = True,
):
    """
    If apply_metrics is True (default), will call get_all_regions_valid_cases_and_ratios on df.
    One stacked bar per region:
      • Lower segment  = valid_cases_count × close_reason_ratio
      • Upper segment  = remainder (missing part)
      • Ratio shown as % label inside the lower segment.
    Returns a tuple: (fig, insight_dict) where insight_dict is a dict of region: ratio.
    """
    import plotly.graph_objects as go
    if apply_metrics:
        from transform.metrics import get_all_regions_valid_cases_and_ratios
        df = get_all_regions_valid_cases_and_ratios(df)
    if df.empty or count_col not in df or ratio_col not in df:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, font_size=20, xref="paper", yref="paper")
        fig.update_layout(title=title)
        return fig, {}
    fig = go.Figure()
    valid_counts = (df[count_col] * df[ratio_col]).round().astype(int)
    fig.add_trace(go.Bar(
        x=df[region_col],
        y=valid_counts,
        name="Close-Reason",
        marker_color="orange",
        text=[f"{count} ({ratio:.1%})" for count, ratio in zip(valid_counts, df[ratio_col])],
        textposition="inside"
    ))
    fig.add_trace(go.Bar(
        x=df[region_col],
        y=df[count_col] - valid_counts,
        name="Missing",
        marker_color="blue",
        text=[f"{int(v)}" for v in (df[count_col] - valid_counts)],
        textposition="outside"
    ))
    fig.update_layout(
        barmode="stack",
        title=title,
        xaxis_title="Region",
        yaxis_title="Number of Cases",
        legend_title="Type",
        margin=dict(t=60, l=50, r=30, b=40),
        template="simple_white"
    )
    # Prepare insight dict
    insight = {str(region).upper(): float(ratio) for region, ratio in zip(df[region_col], df[ratio_col])}
    return fig, insight


def plot_articles_created_per_employee_by_region(df: pd.DataFrame, start, end, region_col: str = "region"):
    """
    Bar chart: Articles created per employee by region, sorted descending.
    """
    from src.transform.metrics import count_created_articles
    TEAM_SIZES = {
        "AMERICAS": 92,
        "EMEA": 46,
        "APJ": 41
    }
    df = df.copy()
    df[region_col] = df[region_col].astype(str).str.strip().str.upper()
    regions = [r for r in TEAM_SIZES.keys() if r in df[region_col].unique()]
    created_per_employee = []
    for region in regions:
        region_df = df[df[region_col] == region]
        created_count = count_created_articles(region_df, start, end)
        team_size = TEAM_SIZES[region]
        per_employee = created_count / team_size if team_size else 0
        created_per_employee.append(per_employee)
    # Sort regions and values descending by created_per_employee
    region_vals = list(zip(regions, created_per_employee))
    region_vals.sort(key=lambda x: x[1], reverse=True)
    sorted_regions = [r for r, v in region_vals]
    sorted_values = [v for r, v in region_vals]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sorted_regions,
        y=sorted_values,
        name='Articles Created per Employee',
        # No custom colors
        text=[f"{v:.2f}" for v in sorted_values],
        textposition='outside',
        marker_line_width=2,
        marker_line_color='#222'
    ))
    fig.update_layout(
        title={
            'text': 'Articles Created per Employee by Region',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=22, family='Arial Black')
        },
        xaxis_title='',
        yaxis_title='Articles Created per Employee',
        font=dict(family="Arial", size=16),
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='#FAFAFA',
        yaxis=dict(showgrid=True, gridcolor='#E5ECF6', zeroline=True, zerolinecolor='#B0B0B0'),
        xaxis=dict(showline=False, showticklabels=True, tickvals=sorted_regions, ticktext=sorted_regions),
        showlegend=False,
        margin=dict(t=80, l=60, r=40, b=120)
    )
    fig.update_traces(hovertemplate='<b>%{y:.2f}</b>')
    return fig


def plot_articles_created_per_coach_by_region(df: pd.DataFrame, start, end, region_col: str = "region"):
    """
    Bar chart: Articles created per coach by region, sorted descending.
    """
    from src.transform.metrics import count_created_articles
    COACHES_SIZES = {
        "AMERICAS": 5,
        "EMEA": 7,
        "APJ": 3
    }
    df = df.copy()
    df[region_col] = df[region_col].astype(str).str.strip().str.upper()
    regions = [r for r in COACHES_SIZES.keys() if r in df[region_col].unique()]
    created_per_coach = []
    for region in regions:
        region_df = df[df[region_col] == region]
        created_count = count_created_articles(region_df, start, end)
        coach_size = COACHES_SIZES[region]
        per_coach = created_count / coach_size if coach_size else 0
        created_per_coach.append(per_coach)
    # Sort regions and values descending by created_per_coach
    region_vals = list(zip(regions, created_per_coach))
    region_vals.sort(key=lambda x: x[1], reverse=True)
    sorted_regions = [r for r, v in region_vals]
    sorted_values = [v for r, v in region_vals]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sorted_regions,
        y=sorted_values,
        name='Articles Created per Coach',
        # No custom colors
        text=[f"{v:.2f}" for v in sorted_values],
        textposition='outside',
        marker_line_width=2,
        marker_line_color='#222'
    ))
    fig.update_layout(
        title={
            'text': 'Articles Created per Coach by Region',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=22, family='Arial Black')
        },
        xaxis_title='',
        yaxis_title='Articles Created per Coach',
        font=dict(family="Arial", size=16),
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='#FAFAFA',
        yaxis=dict(showgrid=True, gridcolor='#E5ECF6', zeroline=True, zerolinecolor='#B0B0B0'),
        xaxis=dict(showline=False, showticklabels=True, tickvals=sorted_regions, ticktext=sorted_regions),
        showlegend=False,
        margin=dict(t=80, l=60, r=40, b=120)
    )
    fig.update_traces(hovertemplate='<b>%{y:.2f}</b>')
    return fig



# ───────────────────────────── LINE CHARTS ─────────────────────────────


def plot_open_cases_week_over_week_by_region(df_cases, title="Open Cases Week over Week by Region", figsize=(10, 6)):
    """
    Line chart: Open cases week over week for each region.
    Only show x-ticks for dates with data (the 1st, 8th, 15th, 22nd).
    """
    import plotly.graph_objects as go
    from transform.metrics import open_cases_week_over_week_by_region
    df = open_cases_week_over_week_by_region(df_cases)
    if df.empty or "week" not in df or "REGION" not in df or "open_cases_count" not in df:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, font_size=20, xref="paper", yref="paper")
        fig.update_layout(title=title)
        return fig
    # Ensure week column is string formatted as YYYY-MM-DD
    df = df.copy()
    if pd.api.types.is_datetime64_any_dtype(df["week"]):
        df["week"] = df["week"].dt.strftime("%Y-%m-%d")
    else:
        df["week"] = df["week"].astype(str)
    fig = go.Figure()
    for region, group in df.groupby("REGION"):
        fig.add_trace(go.Scatter(
            x=group["week"],
            y=group["open_cases_count"],
            mode="lines+markers+text",
            name=region,
            text=group["open_cases_count"],
            textposition="top center"
        ))
    fig.update_layout(
        title=title,
        xaxis_title="Week",
        yaxis_title="Open Cases Count",
        legend_title="Region",
        margin=dict(t=60, l=50, r=30, b=40),
        template="simple_white"
    )
    # Only show x-ticks for dates with data (the 1st, 8th, 15th, 22nd)
    unique_weeks = sorted(df["week"].unique())
    fig.update_xaxes(
        tickvals=unique_weeks,
        ticktext=unique_weeks,
        tickformat="%Y-%m-%d"
    )
    return fig


def plot_ratio_series(
    df: pd.DataFrame,
    title: str = "Close-Reason Ratio – Last 6 Months",
    as_bar: bool = False,
    start_month: str = None,
    end_month: str = None,
    n: int = 6,
):
    """
    Line or bar chart for close-reason ratio by month and region.
    """
    # Filter by month range
    if start_month and end_month:
        months = pd.period_range(start=start_month, end=end_month, freq='M').astype(str)
        df = df[df["month"].isin(months)]
    else:
        months_sorted = sorted(df["month"].unique())[-n:]
        df = df[df["month"].isin(months_sorted)]

    # Filter out unwanted regions (exclude any region containing 'ADMIN')
    df = df[~df["region"].str.upper().str.contains("ADMIN")]

    if as_bar:
        fig = px.bar(
            df, x="month", y="ratio", color="region",
            barmode="group", text_auto=".0%", title=title,
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
    else:
        fig = px.line(
            df, x="month", y="ratio", color="region",
            markers=True, title=title,
            color_discrete_sequence=px.colors.qualitative.Safe,
            line_group="region",
        )
        fig.update_traces(line_width=3, mode="lines+markers")

    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Close-Reason Ratio",
        hovermode="x unified",
        template="simple_white",
        margin=dict(t=60, l=50, r=30, b=40),
    )
    return fig


# ───────────────────────────── HELPERS ──────────────────────��──────


def format_kcs_engagement_by_region(df, region_col="region", ratio_col="close_reason_ratio"):
    """
    Returns a string summarizing KCS Engagement ratios by region, sorted alphabetically by region.
    Example: "KCS Engagement by Region: AMERICAS: 83.8%, APJ: 93.4%, EMEA: 90.1%"
    """
    if df.empty or region_col not in df or ratio_col not in df:
        return "No KCS Engagement data available by region."
    # Prepare region-ratio pairs, sort by region name
    region_ratios = sorted(
        zip(df[region_col].astype(str).str.upper(), df[ratio_col]),
        key=lambda x: x[0]
    )
    summary = [f"{region}: {ratio*100:.1f}%" for region, ratio in region_ratios]
    return "KCS Engagement by Region: " + ", ".join(summary)

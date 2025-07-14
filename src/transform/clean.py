import pandas as pd

def clean_articles(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # select & rename
    wanted = {
        "PUBLISHED_BY_NAME"   : "publisher",
        "PUBLISHED_BY_REGION" : "region",
        "PUBLIC_KB_VIEWCOUNT" : "views_by_customers",
        "ARTICLE_NUMBER"      : "article_id",
        "ARTICLE_FIRST_PUBLISHED_DATE" : "published_at",
        "DAYS_TO_PUBLISH"     : "days_to_publish",
        "ARTICLE_TYPE"        : "article_type",
        "PUBLISH_STATUS"      : "publish_status",
        "INTERNAL"            : "internal",
        "ARTILE_TITLE"        : "title",
        "COMMUNITY_ARTICLE_URL" : "community_article_url",
        "ARTICLE_CASE_ATTACH_COUNT" : "article_attach_count",
        "CREATOR_REGION"      : "creator_region",
        "ARTICLE_CREATED_DATE": "created_at",
        "CREATOR_NAME" : "creator_name",
        "VISIBLE_IN_CUSTOMER_PORTAL" : "visible_to_customers",
        "VERSION_IS_LATEST" : "version_is_latest",
        "PUBLISHED_BY_NAME" : "published_by_name",

    }
    df = df[wanted.keys()].rename(columns=wanted)

    # dtypes
    df["views_by_customers"] = df["views_by_customers"].fillna(0).astype(int)

    return df

def clean_cases(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    wanted = {
        "CASE_NUMBER" : "case_id", # unique identifier for the case
        "CREATED_DATE" : "created_date", # date when the case was created
        "CLOSED_DATE" : "closed_date", # date when the case was closed
        "REGION" : "region", # region of the case
        "PRODUCT" : "product", # product related to the case
        "OWNER_NAME" : "owner_name", # the one who actually owns the case
        "CREATED_BY_REGION" : "created_by_region", # the region of the person who published case if there is one
        "AGE" : "age", # age of the case in days
        "CUSTOMER_ACCOUNT_REGION" : "customer_account_region", # region of the customer account
        "ATTACHED_ARTICLE_COUNT" : "attached_article_count", # number of articles attached to the case
        "CLOSE_REASON" : "close_reason", # reason for closing the case
        "STATUS" : "status", # current status of the case
        "RECORD_TYPE" : "case_record_type",
        "OWNER_ROLE" : "owner_role",# type of the case record
        "OWNER_COMPANY" : "owner_company", # company of the case owner

    }
    df = df[wanted.keys()].rename(columns=wanted)
    return df
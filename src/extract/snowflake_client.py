"""Thin wrapper around the native Snowflake connector."""
from snowflake.connector import connect
from config.settings import SF_CREDS

def get_connection():
    """
    Return an autocommit Snowflake connection.

    Usage:
        with get_connection() as cn, cn.cursor() as cur:
            cur.execute("SELECT 1")
    """
    return connect(**SF_CREDS, autocommit=True)

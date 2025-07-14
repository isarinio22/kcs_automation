from dotenv import load_dotenv

load_dotenv()

import os
SF_CREDS = {
    "account":        os.getenv("SNOWFLAKE_ACCOUNT"),
    "user":           os.getenv("SNOWFLAKE_USER"),
    "password":       os.getenv("SNOWFLAKE_PASSWORD", ""),   # empty ok for SSO
    "authenticator":  os.getenv("SNOWFLAKE_AUTHENTICATOR", "snowflake"),
    "role":           os.getenv("SNOWFLAKE_ROLE"),
    "warehouse":      os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database":       os.getenv("SNOWFLAKE_DATABASE"),
    "schema":         os.getenv("SNOWFLAKE_SCHEMA"),
}

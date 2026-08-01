import struct
import pyodbc
from azure.identity import ClientSecretCredential
from dotenv import load_dotenv
import os

load_dotenv()

SQL_COPT_SS_ACCESS_TOKEN = 1256


def get_access_token():
    credential = ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )
    token = credential.get_token("https://database.windows.net/.default")
    return token.token


def get_connection():
    server = os.environ["AZURE_SQL_SERVER"]
    database = os.environ["AZURE_SQL_DATABASE"]

    token = get_access_token()
    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={server};"
        f"Database={database};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )
    conn = pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn


def run_query(sql):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return columns, [list(row) for row in rows]
    finally:
        conn.close()


def get_schema_info():
    sql = """
    SELECT
        t.TABLE_SCHEMA,
        t.TABLE_NAME,
        c.COLUMN_NAME,
        c.DATA_TYPE,
        c.IS_NULLABLE
    FROM INFORMATION_SCHEMA.TABLES t
    JOIN INFORMATION_SCHEMA.COLUMNS c
        ON t.TABLE_NAME = c.TABLE_NAME AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
    WHERE t.TABLE_TYPE = 'BASE TABLE'
    ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
    """
    return run_query(sql)

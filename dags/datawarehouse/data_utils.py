from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

table = "yt_api"

def get_conn_cursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="elt_db")
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur

def close_conn_cur(conn, cur):
    cur.close()
    conn.close()

def create_schema(schema):
    conn, cur = get_conn_cursor()
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    conn.commit()
    close_conn_cur(conn, cur)

def create_table(schema):
    conn, cur = get_conn_cursor()

    if schema == 'staging':
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table}(
            video_id VARCHAR(11) PRIMARY KEY NOT NULL,
            video_title TEXT NOT NULL,
            upload_date TIMESTAMP NOT NULL,
            duration VARCHAR NOT NULL,
            video_views INT,
            like_count INT,
            comment_count INT);"""
    else:
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table}(
            video_id VARCHAR(11) PRIMARY KEY NOT NULL,
            video_title TEXT NOT NULL,
            upload_date TIMESTAMP NOT NULL,
            duration VARCHAR NOT NULL,
            video_type VARCHAR(100) NOT NULL,
            video_views INT,
            like_count INT,
            comment_count INT);"""

    cur.execute(table_sql)
    conn.commit()
    close_conn_cur(conn, cur)

def get_video_ids(cur, schema):
    try:
        cur.execute(f"SELECT video_id FROM {schema}.{table};")
        ids = cur.fetchall()
        return [row['video_id'] for row in ids]
    except Exception as e:
        logger.error(f"Error getting video ids: {e}")
        return []
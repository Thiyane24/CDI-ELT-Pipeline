from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2 import RealDictCursor

def get_conn_cursor():
    hook= PostgresHook(postgres_conn_id= "postgres_db_yt_elt", database="elt_db")
    
    conn= hook.get_conn()
    cur = conn.cursor(cursfor_factory= RealDictCursor)
    return conn, cur

def close_conn_cur(conn,cur):
    cur.close()
    conn.close()
    
def create_schema(schema):
    conn,cur= get_conn_cursor()
     
    schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema}";
    cur.execute(schema_sql)
    conn.commit()
    close_conn_cur(conn,cur)
    
table = "yt_api"
    
def create_table(schema):
    conn,cur= get_conn_cursor()
    
    if schema == 'staging':
        table_sql=f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table}(
            'Video_Id' VARCHAR(11) PRIMARY KEY NOT NULL,
            'Video_title' TEXT NOT NULL,
            'Upload_date' TIMESTAMP NOT NULL,
            'Duration' VARCHAR NOT NULL,
            'Video_views' INT,
            'Like_Count' INT,
            'Comment_Count' INT);"""
    else:
        table_sql=f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table}(
            'Video_Id' VARCHAR(11) PRIMARY KEY NOT NULL,
            'Video_title' TEXT NOT NULL,
            'Upload_date' TIMESTAMP NOT NULL,
            'Duration' VARCHAR NOT NULL,
            'Video_type' VARCHAR(100) NOT NULL
            'Video_views' INT,
            'Like_Count' INT,
            'Comment_Count' INT);"""
    conn.execute(table_sql)
    conn.commit()
    close_conn_cur(conn,cur)
    
def get_video_ids(cur,schema):
    cur.execute(f"""SELECT 'Video_Id' FROM {schema}.{table};""")
    
    ids= cur.fetchall()
    
    video_ids= [row['Video_Id']for row in ids]
    
    return video_ids
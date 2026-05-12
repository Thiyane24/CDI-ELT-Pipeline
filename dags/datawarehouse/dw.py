from datawarehouse.data_utils import get_conn_cursor, close_conn_cur, create_schema, create_table, get_video_ids
from datawarehouse.data_loading import load_path
from datawarehouse.data_modification import insert_rows, update_rows, delete_rows
from datawarehouse.transformation import transform_data

import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)
table = "yt_api"

@task
def staging_table():
    schema = 'staging'
    conn, cur = None, None

    try:
        conn, cur = get_conn_cursor()
        YT_data = load_path()

        create_schema(schema)
        create_table(schema)

        table_ids = get_video_ids(cur, schema)

        for row in YT_data:
            if not row.get('video_id'):
                logger.warning(f"Skipping row with missing video_id: {row}")
                continue
            if len(table_ids) == 0:
                insert_rows(cur, conn, schema, row)
            else:
                if row['video_id'] in table_ids:
                    update_rows(cur, conn, schema, row)
                else:
                    insert_rows(cur, conn, schema, row)

        ids_in_json = {row['video_id'] for row in YT_data if row.get('video_id')}
        ids_to_delete = set(table_ids) - ids_in_json
        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)

        logger.info("Data loaded successfully into staging table.")

    except Exception as e:
        logger.error(f"Error loading data into staging table: {e}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn and cur:
            close_conn_cur(conn, cur)


@task
def core_table():
    schema = 'core'
    conn, cur = None, None

    try:
        conn, cur = get_conn_cursor()
        create_schema(schema)
        create_table(schema)
        table_ids = get_video_ids(cur, schema)
        current_ids = set()

        cur.execute(f"SELECT * FROM staging.{table}")
        rows = cur.fetchall()

        for row in rows:
            video_id = row.get('video_id')  # ← lowercase
            if not video_id:
                logger.warning(f"Skipping row with missing video_id: {row}")
                continue

            current_ids.add(video_id)
            transformed_row = transform_data(dict(row))

            if len(table_ids) == 0:
                insert_rows(cur, conn, schema, transformed_row)
            else:
                if video_id in table_ids:
                    update_rows(cur, conn, schema, transformed_row)
                else:
                    insert_rows(cur, conn, schema, transformed_row)

        ids_to_delete = set(table_ids) - current_ids
        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)

        logger.info("Data transformed and loaded successfully into core table.")

    except Exception as e:
        logger.error(f"Error transforming and loading data into core table: {e}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn and cur:
            close_conn_cur(conn, cur)
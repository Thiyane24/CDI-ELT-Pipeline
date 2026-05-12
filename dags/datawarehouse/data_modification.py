import logging

logger = logging.getLogger(__name__)

table = "yt_api"


def insert_rows(cur, conn, schema, row):
    try:
        if schema == 'staging':
            cur.execute(f"""
                INSERT INTO {schema}.{table}
                (video_id, video_title, upload_date, duration, video_views, like_count, comment_count)
                VALUES (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s, %(viewCount)s, %(likeCount)s, %(commentCount)s)
                ON CONFLICT (video_id) DO NOTHING;
            """, row)
        else:
            cur.execute(f"""
                INSERT INTO {schema}.{table}
                (video_id, video_title, upload_date, duration, video_type, video_views, like_count, comment_count)
                VALUES (%(video_id)s, %(video_title)s, %(upload_date)s, %(duration)s, %(video_type)s, %(video_views)s, %(like_count)s, %(comment_count)s)
                ON CONFLICT (video_id) DO NOTHING;
            """, row)
        conn.commit()
        logger.info(f"Inserted row with video_id: {row.get('video_id')}")

    except Exception as e:
        logger.error(f"Error inserting row: {e}")
        raise e


def update_rows(cur, conn, schema, row):
    try:
        if schema == 'staging':
            cur.execute(f"""
                UPDATE {schema}.{table}
                SET video_title = %(title)s,
                    video_views = %(viewCount)s,
                    like_count = %(likeCount)s,
                    comment_count = %(commentCount)s
                WHERE video_id = %(video_id)s
                AND upload_date = %(publishedAt)s;
            """, row)
        else:
            cur.execute(f"""
                UPDATE {schema}.{table}
                SET video_title = %(video_title)s,
                    video_views = %(video_views)s,
                    like_count = %(like_count)s,
                    comment_count = %(comment_count)s
                WHERE video_id = %(video_id)s
                AND upload_date = %(upload_date)s;
            """, row)
        conn.commit()
        logger.info(f"Updated row with video_id: {row.get('video_id')}")

    except Exception as e:
        logger.error(f"Error updating row: {e}")
        raise e


def delete_rows(cur, conn, schema, ids_to_delete):
    try:
        cur.execute(f"DELETE FROM {schema}.{table} WHERE video_id = ANY(%s);", (list(ids_to_delete),))
        conn.commit()
        logger.info(f"Deleted rows with video_ids: {ids_to_delete}")

    except Exception as e:
        logger.error(f"Error deleting rows with video_ids: {ids_to_delete} - {e}")
        raise e
    
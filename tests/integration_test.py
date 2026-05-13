import requests
import pytest
import psycopg2


def test_api_response(airflow_variable):
    api_key = airflow_variable("API_KEY")
    channel_handle = airflow_variable("CHANNEL_HANDLE")
    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}"

    try:
        response = requests.get(url)
        assert response.status_code ==200
    
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API request failed: {e}")
        
def test_pg_conn(real_pg_conn):
   cursor = None
   
   try: 
       cursor = real_pg_conn.cursor()
       cursor.execute("SELECT 1")
       result = cursor.fetchone()
       assert result[0] == 1
   except psycopg2.Error as e:
         pytest.fail(f"Database connection test failed: {e}")
   finally:
       if cursor is not None:
           cursor.close()
           
    
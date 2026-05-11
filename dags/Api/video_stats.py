import requests
import json
import pandas as pd
import os
from datetime import datetime
from airflow.decorators import task
from airflow.models import Variable

api_key = Variable.get("API_KEY")
CHANNEL_HANDLE = Variable.get("CHANNEL_HANDLE")


@task
def getPlaylistId():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={api_key}"

        response = requests.get(url)
        data = response.json()
        print(json.dumps(data, indent=4))
        new_data = []

        if response.status_code == 200:
            for item in data['items']:
                flat_dict = {
                    'id': item['id'],
                    'etag': item['etag'],
                    'likes': item['contentDetails']['relatedPlaylists']['likes'],
                    'playlist_id': item['contentDetails']['relatedPlaylists']['uploads']
                }
                new_data.append(flat_dict)
            df = pd.DataFrame(new_data)
            print(df['playlist_id'])
            return df['playlist_id'].iloc[0]
        else:
            print(response.status_code)
            raise Exception("Status code is not 200")

    except requests.exceptions.RequestException as e:
        raise e


max_results = 50


@task
def getVideoResult(playlist_id):
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={api_key}"

    video_ids = []
    next_page_token = None

    try:
        while True:
            url = base_url
            if next_page_token:
                url += f"&pageToken={next_page_token}"

            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                for item in data['items']:
                    video_ids.append(item['contentDetails']['videoId'])

                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
            else:
                print(f"Error: {response.status_code}")
                break

        print(f"Total videos fetched: {len(video_ids)}")
        return video_ids

    except requests.exceptions.RequestException as e:
        raise e
    except KeyError as e:
        print(f"Unexpected response structure: {e}")


@task
def video_data(video_ids):
    extracted_data = []

    def batch_lst(video_id_lst, batch_size):
        for i in range(0, len(video_id_lst), batch_size):
            yield video_id_lst[i: i + batch_size]

    try:
        for batch in batch_lst(video_ids, max_results):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={video_ids_str}&key={api_key}"
            response = requests.get(url)
            data = response.json()
            print(f"Batch size: {len(batch)}")
            print(f"Items returned: {len(data.get('items', []))}")

            for item in data.get('items', []):
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_dict = {
                    'video_id': item['id'],
                    'title': snippet['title'],
                    'publishedAt': snippet['publishedAt'],
                    'duration': contentDetails['duration'],
                    'viewCount': statistics.get('viewCount', None),
                    'likeCount': statistics.get('likeCount', None),
                    'commentCount': statistics.get('commentCount', None)
                }
                extracted_data.append(video_dict)

    except requests.exceptions.RequestException as e:
        raise e

    df2 = pd.DataFrame(extracted_data)
    print(df2)


    load_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs('/opt/airflow/Data', exist_ok=True)
    df2.to_json(f'/opt/airflow/Data/video_data_{load_id}.json', orient='records', indent=4)
    print(f"Saved to /opt/airflow/Data/video_data_{load_id}.json")

    return df2.to_dict(orient='records')


if __name__ == "__main__":
    playlist_id = getPlaylistId()
    video_ids = getVideoResult(playlist_id)
    video_data(video_ids)
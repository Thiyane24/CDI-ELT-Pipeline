import requests
import json
import pandas as pd
import os 
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")
api_key = os.getenv("API_KEY")
channel= "Conversasdeit"
def getPlaylistId():
  try:
   url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel}&key={api_key}"
  

   response = requests.get(url)
   data = response.json()
   print (json.dumps(data, indent=4))
   new_data= []
  
#flatten the nested json
   if response.status_code == 200:
        for item in data['items']:
            flat_dict= {
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
   

max_results=50



#gets the video IDs
def getVideoResult(playlist_id):
    base_url= f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={api_key}"
    
    
    
    try: 
        response1 = requests.get(base_url)
        data1= response1.json()
        print(json.dumps(data1, indent=4))
        print("\n")
        video_ids = []
        if response1.status_code==200:
            for items in data1['items']:
                video_ids.append(items['contentDetails']['videoId'])
                
            df1 = pd.DataFrame(video_ids, columns=['videoId'])
            print(df1)
            return df1
        
        else:
            print(response1.status_code)
            
        
    except requests.exceptions.RequestException as e:
        raise e
    except KeyError as e:
        print(f"Unexpected response structure: {e}")        
    
    

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
            print(json.dumps(data, indent=4)) 
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
    return df2   
    

 
if __name__ == "__main__":
    playlist_id= getPlaylistId()
    video_ids = getVideoResult(playlist_id)
    video_data(video_ids['videoId'].tolist()) 
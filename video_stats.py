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
        
   else:
       print(response.status_code)
       raise Exception("Status code is not 200")

   print(df['playlist_id'])
  except requests.exceptions.RequestException as e:
       raise e
  
if __name__ == "__main__":
    getPlaylistId()
import json
from datetime import datetime
import logging
from Api.video_stats import load_id

logger= logging.getLogger(__name__)
def load_path():
    
  filepath= f"./Data/video_data_{load_id}.json"

  try:
      logger.info(f"Processing the file: video_data_{load_id}.json")
      with open (filepath, 'r', encoding='utf-8') as raw_data:
        data = json.load(raw_data)
      return data
  
  except FileNotFoundError:
      logger.error(f"File not found {filepath}")
      raise
  except json.JsonDecoderError:
      logger.error(f"Invalid Json format in file: {filepath}")
      raise
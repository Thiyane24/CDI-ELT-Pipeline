import json
import os
import logging

logger = logging.getLogger(__name__)

def load_path():
   
    bronze_dir = '/opt/airflow/Data'

    try:
        files = [f for f in os.listdir(bronze_dir) if f.startswith('video_data_') and f.endswith('.json')]

        if not files:
            raise FileNotFoundError(f"No video_data JSON files found in {bronze_dir}")

        
        latest_file = max(files)
        filepath = os.path.join(bronze_dir, latest_file)

        logger.info(f"Processing the file: {latest_file}")
        with open(filepath, 'r', encoding='utf-8') as raw_data:
            data = json.load(raw_data)
        return data

    except FileNotFoundError:
        logger.error(f"File not found in {bronze_dir}")
        raise
    except json.JSONDecodeError: 
        logger.error(f"Invalid JSON format in file: {filepath}")
        raise
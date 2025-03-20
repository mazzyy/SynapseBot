"""
Helper functions for the Airdrop Automation Tool
"""
import os
import logging
import json
import time
import random
from pathlib import Path

from config.settings import BASE_DIR, COMPLETED_AIRDROPS_FILE

logger = logging.getLogger(__name__)

def create_env_template():
    """Create a template .env file if it doesn't exist"""
    env_path = os.path.join(BASE_DIR, '.env')
    
    if not os.path.exists(env_path):
        try:
            with open(env_path, 'w') as f:
                f.write("""# OpenAI API Key (required for AI assistance)
OPENAI_API_KEY=your_openai_api_key_here

# Social Media Credentials
TELEGRAM_USERNAME=your_telegram_username
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
DISCORD_USERNAME=your_discord_email
DISCORD_PASSWORD=your_discord_password
YOUTUBE_EMAIL=your_youtube_email
YOUTUBE_PASSWORD=your_youtube_password
""")
            logger.info("Created .env template file")
            return True
        except Exception as e:
            logger.error(f"Error creating .env template: {e}")
            return False
    else:
        logger.info(".env file already exists")
        return True

def create_dir_if_not_exists(dir_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            logger.info(f"Created directory: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            return False
    return True

def save_json(data, file_path):
    """Save data to a JSON file"""
    try:
        # Ensure directory exists
        dir_path = os.path.dirname(file_path)
        create_dir_if_not_exists(dir_path)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved data to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False

def load_json(file_path, default=None):
    """Load data from a JSON file"""
    default = default if default is not None else {}
    
    if not os.path.exists(file_path):
        logger.debug(f"File not found: {file_path}, returning default value")
        return default
        
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {file_path}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return default

def get_completed_airdrops():
    """Get the list of completed airdrops"""
    return load_json(COMPLETED_AIRDROPS_FILE, {})

def mark_airdrop_completed(airdrop_name, status="success"):
    """Mark an airdrop as completed"""
    completed = get_completed_airdrops()
    completed[airdrop_name] = {
        'completed_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': status
    }
    return save_json(completed, COMPLETED_AIRDROPS_FILE)

def is_airdrop_completed(airdrop_name):
    """Check if an airdrop has been completed"""
    completed = get_completed_airdrops()
    return airdrop_name in completed

def random_sleep(min_seconds, max_seconds=None):
    """Sleep for a random period between min and max seconds"""
    if max_seconds is None:
        max_seconds = min_seconds * 1.5
        
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)
    return sleep_time

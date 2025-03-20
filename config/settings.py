"""
Configuration settings for the Airdrop Automation Tool
"""
import os
import logging
from logging.handlers import RotatingFileHandler

# Browser Settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
BROWSER_TIMEOUT = 30  # seconds

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# File names
COMPLETED_AIRDROPS_FILE = os.path.join(DATA_DIR, 'completed_airdrops.json')

# Random wait times (in seconds)
WAIT_TIMES = {
    'short': (1, 3),
    'medium': (2, 5),
    'long': (3, 7),
    'page_load': (3, 6),
    'human_like': (0.5, 2),
}

# XPath selectors for common elements
SELECTORS = {
    'all_airdrops_tab': "//div[text()='All airdrops']",
    'airdrop_cards': "//div[contains(@class, 'airdrop-card')]",
    'task_items': "//div[contains(@class, 'task-item') and contains(., '(Mandatory)')]",
    'telegram_button': ".//a[contains(@href, 'telegram.org') or contains(@href, 't.me')]",
    'twitter_button': ".//a[contains(@href, 'twitter.com') or contains(@href, 'x.com')]",
    'discord_button': ".//a[contains(@href, 'discord.com') or contains(@href, 'discord.gg')]",
    'youtube_button': ".//a[contains(@href, 'youtube.com')]",
    'follow_button': "//span[text()='Follow']",
    'subscribe_button': "//button[contains(@aria-label, 'Subscribe')]",
    'task_completed': ".//div[contains(@class, 'completed') or contains(@class, 'check')]",
}

# OpenAI API settings
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 150

def setup_logging():
    """Configure logging settings"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_file = os.path.join(LOG_DIR, 'airdrop_bot.log')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Setup file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
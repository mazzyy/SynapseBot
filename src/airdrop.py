"""
Airdrop selector and data handling
"""
import os
import json
import logging
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from src.tasks.telegram import TelegramTask
from src.tasks.base import BaseTask
from config.settings import SELECTORS, COMPLETED_AIRDROPS_FILE

logger = logging.getLogger(__name__)

class AirdropManager:
    """Manages airdrop selection and task execution"""
    
    def __init__(self, browser):
        """
        Initialize the airdrop manager
        
        Args:
            browser (BrowserManager): Browser manager instance
        """
        self.browser = browser
        self.completed_airdrops = self._load_completed_airdrops()
        
        # Initialize task handlers
        self.task_handlers = {
            'telegram': TelegramTask(browser),
            'visit': None  # Will be set dynamically based on page structure
        }
        
    def _load_completed_airdrops(self):
        """Load the list of already completed airdrops"""
        if not os.path.exists(COMPLETED_AIRDROPS_FILE):
            return {}
            
        try:
            with open(COMPLETED_AIRDROPS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Could not load completed airdrops file, creating new one")
            return {}
            
    def _save_completed_airdrops(self):
        """Save the list of completed airdrops"""
        try:
            with open(COMPLETED_AIRDROPS_FILE, 'w') as f:
                json.dump(self.completed_airdrops, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving completed airdrops: {e}")
        
    def navigate_to_listing(self, url):
        """Navigate to the airdrop listing page"""
        self.browser.get(url)
        
        # Try to click on "All airdrops" tab if it exists
        all_airdrops_tab = self.browser.wait_for_element(
            By.XPATH, 
            SELECTORS['all_airdrops_tab']
        )
        
        if all_airdrops_tab:
            self.browser.click(all_airdrops_tab)
        
    def get_available_airdrops(self):
        """
        Get list of all available airdrops from the current page
        
        Returns:
            list: Airdrop info dictionaries including reference to element
        """
        airdrop_elements = self.browser.wait_for_elements(
            By.XPATH, 
            SELECTORS['airdrop_cards']
        )
        
        if not airdrop_elements:
            logger.warning("No airdrop elements found on page")
            return []
            
        airdrops = []
        for element in airdrop_elements:
            try:
                # These XPaths will need adjustment based on the actual site structure
                name = element.find_element(By.XPATH, ".//div[contains(@class, 'airdrop-name')]").text
                
                # Some airdrop elements might have time and reward info
                try:
                    time_left = element.find_element(By.XPATH, ".//div[contains(@class, 'time-left')]").text
                except NoSuchElementException:
                    time_left = "Unknown"
                    
                try:
                    reward = element.find_element(By.XPATH, ".//div[contains(@class, 'reward')]").text
                except NoSuchElementException:
                    reward = "Unknown"
                
                airdrops.append({
                    'name': name,
                    'time_left': time_left,
                    'reward': reward,
                    'element': element
                })
            except NoSuchElementException as e:
                logger.warning(f"Error parsing airdrop element: {e}")
                
        logger.info(f"Found {len(airdrops)} available airdrops")
        return airdrops
        
    def select_airdrop(self, airdrop_name=None):
        """
        Select a specific airdrop by name or the first available one
        
        Args:
            airdrop_name (str, optional): Name of the airdrop to select
            
        Returns:
            str: Name of the selected airdrop, or None if none selected
        """
        airdrops = self.get_available_airdrops()
        
        if not airdrops:
            logger.error("No airdrops available")
            return None
            
        selected_airdrop = None
        
        if airdrop_name:
            # Try to find the specific airdrop
            for airdrop in airdrops:
                if airdrop_name.lower() in airdrop['name'].lower():
                    selected_airdrop = airdrop
                    break
                    
            if not selected_airdrop:
                logger.warning(f"Airdrop '{airdrop_name}' not found, selecting first available")
                selected_airdrop = airdrops[0]
        else:
            # Select the first one
            selected_airdrop = airdrops[0]
            
        # Check if we've already completed this airdrop
        if selected_airdrop['name'] in self.completed_airdrops:
            logger.info(f"Airdrop '{selected_airdrop['name']}' already completed, skipping")
            return None
            
        # Click on the selected airdrop
        if self.browser.click(selected_airdrop['element']):
            logger.info(f"Selected airdrop: {selected_airdrop['name']}")
            self.browser.random_wait('medium')
            return selected_airdrop['name']
        else:
            logger.error(f"Error clicking on airdrop: {selected_airdrop['name']}")
            return None
    
    def get_task_type(self, task_text):
        """
        Determine the type of task based on the task text
        
        Args:
            task_text (str): Text description of the task
            
        Returns:
            str: Task type identifier ('telegram', 'twitter', etc.)
        """
        task_text = task_text.lower()
        
        if "visit" in task_text and "airdrop page" in task_text:
            return 'visit'
        elif "telegram" in task_text:
            return 'telegram'
        else:
            return 'unknown'
            
    def complete_all_tasks(self, airdrop_name):
        """
        Complete all mandatory tasks for the selected airdrop
        
        Args:
            airdrop_name (str): Name of the airdrop to complete tasks for
            
        Returns:
            bool: True if all tasks completed successfully, False otherwise
        """
       
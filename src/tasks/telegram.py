"""
Telegram task handler for airdrop requirements
"""
import os
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from src.tasks.base import BaseTask
from src.utils.ai import get_ai_assistance
from config.settings import SELECTORS

logger = logging.getLogger(__name__)

class TelegramTask(BaseTask):
    """Handles Telegram-specific task requirements"""
    
    def complete_task(self, task_element):
        """
        Complete a 'Join group on Telegram' task
        
        Args:
            task_element: The Telegram task element
            
        Returns:
            bool: True if task completed successfully, False otherwise
        """
        # First expand the task if needed
        if not self.expand_task(task_element):
            return False
        
        try:
            # Find the Telegram button/link
            telegram_button = task_element.find_element(
                By.XPATH, 
                SELECTORS['telegram_button']
            )
            
            if not telegram_button:
                logger.warning("No Telegram button found")
                return False
            
            # Get the link URL for AI assistance
            telegram_url = telegram_button.get_attribute('href')
            
            # Use AI to get information about the Telegram group
            telegram_info = get_ai_assistance(
                f"Analyze this Telegram group link: {telegram_url}. "
                f"What is this group about? Is it related to a cryptocurrency project? "
                f"What should I expect when joining?"
            )
            
            logger.info(f"Telegram group info from AI: {telegram_info}")
            
            # Execute action in a new tab
            def telegram_action():
                """Action to perform in the Telegram tab"""
                # Automating Telegram directly is difficult due to their security
                # measures, so we'll just provide instructions via logs
                logger.info(f"Manual action required: Join Telegram group at {telegram_url}")
                
                # Check if we need to log in
                if "login" in self.browser.driver.current_url or "Login" in self.browser.driver.page_source:
                    username = os.getenv('TELEGRAM_USERNAME')
                    logger.info(f"Please login with Telegram account: {username}")
                
                # Look for join button - this is informational only
                try:
                    join_button = self.browser.wait_for_element(
                        By.XPATH, 
                        "//button[contains(., 'Join') or contains(., 'join')]",
                        timeout=5
                    )
                    if join_button:
                        logger.info("Join button found on Telegram page")
                except Exception:
                    logger.info("No join button found, you may need to login first")
                
                # Browse the page a bit
                self.browser.human_like_browsing()
                return True
            
            # Execute in new tab
            self.browser.click(telegram_button)
            result = self.browser.new_tab_action(telegram_action)
            
            # Check if task is marked as completed
            return self.check_task_completion(task_element)
            
        except Exception as e:
            logger.error(f"Error completing Telegram task: {e}")
            return False
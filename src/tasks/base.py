"""
Base task class for airdrop tasks
"""
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from config.settings import SELECTORS

logger = logging.getLogger(__name__)

class BaseTask:
    """Base class for all airdrop tasks"""
    
    def __init__(self, browser):
        """
        Initialize the task
        
        Args:
            browser (BrowserManager): Browser manager instance
        """
        self.browser = browser
    
    def expand_task(self, task_element):
        """
        Expand a task if it's collapsed
        
        Args:
            task_element: The task element to expand
            
        Returns:
            bool: True if expanded or already expanded, False otherwise
        """
        try:
            # Check if there's an expand/dropdown button
            expand_button = task_element.find_element(
                By.XPATH, 
                ".//button[contains(@class, 'expand') or contains(@class, 'dropdown')]"
            )
            self.browser.click(expand_button)
            logger.info("Expanded task")
            return True
        except NoSuchElementException:
            # Task might already be expanded
            logger.debug("No expand button found, task may already be expanded")
            return True
        except Exception as e:
            logger.error(f"Error expanding task: {e}")
            return False
    
    def check_task_completion(self, task_element):
        """
        Check if a task is marked as completed
        
        Args:
            task_element: The task element to check
            
        Returns:
            bool: True if task is marked as completed, False otherwise
        """
        try:
            # Look for a checkmark or completed status
            completion_element = task_element.find_element(
                By.XPATH, 
                SELECTORS['task_completed']
            )
            
            if completion_element:
                logger.info("Task marked as completed")
                return True
            return False
        except NoSuchElementException:
            logger.warning("Task not marked as completed automatically")
            
            # Some airdrop platforms require manual verification
            try:
                confirm_button = task_element.find_element(
                    By.XPATH, 
                    ".//button[contains(@class, 'confirm') or contains(., 'Verify') or contains(., 'Done')]"
                )
                self.browser.click(confirm_button)
                logger.info("Clicked task confirmation button")
                self.browser.random_wait('short')
                return True
            except NoSuchElementException:
                logger.warning("No confirmation button found")
                return False
            except Exception as e:
                logger.error(f"Error confirming task: {e}")
                return False
    
    def complete_task(self, task_element):
        """
        Generic method to complete a basic task
        
        Args:
            task_element: The task element to complete
            
        Returns:
            bool: True if task completed successfully, False otherwise
        """
        # First expand the task if needed
        if not self.expand_task(task_element):
            return False
            
        # For the base task, just try to find and click an action button
        try:
            # Generic button finder - this will need customization in child classes
            buttons = task_element.find_elements(
                By.XPATH, 
                ".//a[contains(@href, 'http') or contains(@href, 'https')]"
            )
            
            if not buttons:
                logger.warning("No action buttons found for this task")
                return False
                
            # Click the first button (most likely the main action)
            action_button = buttons[0]
            
            # Store current window handle
            main_window = self.browser.driver.current_window_handle
            
            # Click the button (likely opens in new tab)
            self.browser.click(action_button)
            logger.info("Clicked action button")
            
            # Execute action in new tab
            result = self.browser.new_tab_action(self.browser.human_like_browsing)
            
            # Check if task is marked as completed
            return self.check_task_completion(task_element)
            
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
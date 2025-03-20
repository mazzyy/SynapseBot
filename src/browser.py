"""
Browser setup and management for the Airdrop Automation Tool
"""
import random
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import USER_AGENT, BROWSER_TIMEOUT, WAIT_TIMES

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages browser instance with configurable options"""
    
    def __init__(self, headless=False):
        """
        Initialize browser manager with appropriate options
        
        Args:
            headless (bool): Whether to run browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self._setup_browser()
        self.main_window = None
        
    def _setup_browser(self):
        """Setup Chrome browser with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Common options for stability and to avoid detection
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(f"user-agent={USER_AGENT}")
        
        # Create driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Set default wait time
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, BROWSER_TIMEOUT)
        self.main_window = self.driver.current_window_handle
        
        logger.info("Browser initialized successfully")
        
    def get(self, url):
        """Navigate to the specified URL"""
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        self.random_wait('page_load')
        
    def wait_for_element(self, by, value, timeout=None, condition=EC.presence_of_element_located):
        """
        Wait for an element to be present or specified condition
        
        Args:
            by: Selenium By strategy
            value: Selector value
            timeout: Optional custom timeout
            condition: Expected condition
            
        Returns:
            WebElement if found, None otherwise
        """
        timeout = timeout or BROWSER_TIMEOUT
        try:
            element = WebDriverWait(self.driver, timeout).until(
                condition((by, value))
            )
            return element
        except Exception as e:
            logger.warning(f"Element not found: {by}={value}, Error: {e}")
            return None
            
    def wait_for_elements(self, by, value, timeout=None):
        """Wait for multiple elements to be present"""
        return self.wait_for_element(
            by, 
            value, 
            timeout, 
            condition=EC.presence_of_all_elements_located
        )
            
    def click(self, element):
        """Safely click an element with proper waiting"""
        try:
            element.click()
            self.random_wait('short')
            return True
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False
            
    def new_tab_action(self, action_callback):
        """
        Perform an action in a new tab and return to main window
        
        Args:
            action_callback: Function to execute in the new tab
            
        Returns:
            Result from the action_callback
        """
        # Store current window
        current_window = self.driver.current_window_handle
        
        # Switch to new tab if a new one has opened
        new_window = None
        for window_handle in self.driver.window_handles:
            if window_handle != current_window:
                new_window = window_handle
                self.driver.switch_to.window(new_window)
                break
                
        if not new_window:
            logger.warning("No new tab was opened")
            return None
            
        # Perform the action
        try:
            result = action_callback()
        except Exception as e:
            logger.error(f"Error in new tab: {e}")
            result = None
            
        # Close tab and switch back
        if len(self.driver.window_handles) > 1:
            self.driver.close()
        self.driver.switch_to.window(current_window)
        
        return result
            
    def scroll_page(self, direction="down", amount=None):
        """
        Scroll the page in the specified direction
        
        Args:
            direction (str): 'up' or 'down'
            amount (int): Scroll amount in pixels, random if None
        """
        if amount is None:
            amount = random.randint(300, 700) * (-1 if direction == "up" else 1)
        elif direction == "up":
            amount = -abs(amount)
            
        self.driver.execute_script(f"window.scrollBy(0, {amount});")
        self.random_wait('human_like')
            
    def human_like_browsing(self):
        """Simulate human-like browsing behavior with scrolling"""
        # Scroll down several times
        for _ in range(random.randint(2, 5)):
            self.scroll_page("down")
            
        # Sometimes scroll back up
        if random.random() > 0.3:
            for _ in range(random.randint(1, 3)):
                self.scroll_page("up")
                
    def random_wait(self, wait_type='short'):
        """
        Wait for a random time based on the specified wait type
        
        Args:
            wait_type (str): 'short', 'medium', 'long', 'page_load', or 'human_like'
        """
        min_wait, max_wait = WAIT_TIMES.get(wait_type, (1, 3))
        wait_time = random.uniform(min_wait, max_wait)
        time.sleep(wait_time)
        
    def __enter__(self):
        """Context manager entry"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")
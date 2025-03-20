#!/usr/bin/env python3
"""
Airdrop Automation Tool - Main Entry Point
"""
import os
import time
import logging
import argparse
from dotenv import load_dotenv

from src.browser import BrowserManager
from src.airdrop import AirdropManager
from config.settings import setup_logging

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Airdrop Automation Tool')
    parser.add_argument(
        '--headless', 
        action='store_true', 
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--airdrop', 
        type=str, 
        help='Target a specific airdrop by name'
    )
    parser.add_argument(
        '--url', 
        type=str, 
        default='https://airdrop.io', 
        help='Airdrop listing URL'
    )
    return parser.parse_args()

def main():
    """Main function to run the airdrop automation"""
    # Parse arguments
    args = parse_arguments()
    
    # Setup environment
    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check if .env file exists with necessary credentials
    if not os.path.exists('.env') or not os.getenv('OPENAI_API_KEY'):
        logger.error("Missing .env file or required credentials")
        from src.utils.helpers import create_env_template
        create_env_template()
        print("\nPlease fill in your credentials in the .env file before running again.")
        return

    try:
        # Initialize browser
        with BrowserManager(headless=args.headless) as browser:
            # Initialize airdrop manager
            airdrop_mgr = AirdropManager(browser)
            
            # Navigate to airdrop listing
            airdrop_mgr.navigate_to_listing(args.url)
            
            # Select specified airdrop or first available
            airdrop_name = airdrop_mgr.select_airdrop(args.airdrop)
            
            if airdrop_name:
                # Complete all tasks for this airdrop
                success = airdrop_mgr.complete_all_tasks(airdrop_name)
                
                if success:
                    logger.info(f"Successfully completed all tasks for {airdrop_name}")
                else:
                    logger.warning(f"Could not complete all tasks for {airdrop_name}")
                    
                # Wait a moment before closing
                time.sleep(3)
            else:
                logger.error("No airdrop was selected or available")

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        
if __name__ == "__main__":
    main()
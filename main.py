# main.py
# Version: 1.0.0
# Description: Main execution script for WordPress automation
# Changelog:
# 1.0.0 - Initial implementation

import os
import sys
import logging
from src.automation_manager import AutomationManager

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/automation.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main execution function"""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting WordPress automation")
        
        # Initialize automation manager
        automation = AutomationManager()
        
        # Get input file from command line or use default
        input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/topics.csv'
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Run automation
        automation.run_automation(input_file)
        
        logger.info("Automation completed successfully")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
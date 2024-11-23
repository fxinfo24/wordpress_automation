# src/utils/logger.py
# Version: 1.0.0
# Description: Custom logger configuration
# Changelog:
# 1.0.0 - Initial implementation

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

class CustomLogger:
    VERSION = "1.0.0"
    
    def __init__(self, name: str, config: dict):
        """Initialize custom logger"""
        self.name = name
        self.config = config
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup and configure logger"""
        # Create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(self.config.get('level', 'INFO'))

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - v%(version)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Create file handler
        log_file = self.config.get('file_path', 'logs/automation.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.get('max_size', 10485760),
            backupCount=self.config.get('backup_count', 5)
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """Get configured logger"""
        return self.logger

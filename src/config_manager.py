# src/config_manager.py
# Version: 1.0.0
# Description: Configuration management and logging setup
# Changelog:
# 1.0.0 - Initial implementation with config validation and logging setup

import os
import json
import logging
import configparser
from typing import Dict, Any
from datetime import datetime

class ConfigManager:
    VERSION = "1.0.0"
    
    def __init__(self, config_file: str = 'config/config.ini'):
        """Initialize configuration manager"""
        self.config_file = config_file
        self.config = self._load_config()
        self._setup_logging()
        self._validate_config()
        
        # Log configuration initialization
        self.logger.info(
            f"ConfigManager v{self.VERSION} initialized with config file: {config_file}"
        )

    def _load_config(self) -> configparser.ConfigParser:
        """Load and parse configuration file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}"
            )
        
        config = configparser.ConfigParser()
        config.read(self.config_file)
        return config

    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log filename with version and date
        log_filename = os.path.join(
            log_dir,
            f'wordpress_automation_v{self.VERSION}_{datetime.now().strftime("%Y%m%d")}.log'
        )
        
        # Configure logging
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - v%(version)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())  # Add console output

    def _validate_config(self) -> None:
        """Validate configuration settings"""
        required_sections = {
            'wordpress': ['url', 'username', 'password'],
            'openai': ['api_key', 'model'],
            'unsplash': ['access_key'],
            'images': ['min_width', 'min_height', 'quality'],
            'content': ['min_word_count', 'max_retries']
        }
        
        missing = []
        for section, keys in required_sections.items():
            if section not in self.config:
                missing.append(f"Missing section: {section}")
                continue
            
            for key in keys:
                if key not in self.config[section]:
                    missing.append(f"Missing key in {section}: {key}")
        
        if missing:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(missing))

    def get_config(self, section: str, key: str) -> str:
        """Get configuration value"""
        try:
            return self.config[section][key]
        except KeyError as e:
            self.logger.error(f"Configuration key not found: {section}.{key}")
            raise KeyError(f"Configuration not found: {section}.{key}") from e

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        try:
            return dict(self.config[section])
        except KeyError as e:
            self.logger.error(f"Configuration section not found: {section}")
            raise KeyError(f"Section not found: {section}") from e

    def save_version_info(self) -> None:
        """Save version information to version control"""
        version_file = os.path.join('version_control', 'versions.json')
        version_info = {
            'timestamp': datetime.now().isoformat(),
            'version': self.VERSION,
            'config_file': self.config_file
        }
        
        try:
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    versions = json.load(f)
            else:
                versions = []
            
            versions.append(version_info)
            
            with open(version_file, 'w') as f:
                json.dump(versions, f, indent=4)
                
            self.logger.info(f"Version information saved: v{self.VERSION}")
            
        except Exception as e:
            self.logger.error(f"Error saving version information: {str(e)}")
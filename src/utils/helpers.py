# src/utils/helpers.py
# Version: 1.0.0
# Description: Helper functions for the automation
# Changelog:
# 1.0.0 - Initial implementation

import os
import json
import hashlib
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

class AutomationHelper:
    VERSION = "1.0.0"
    
    @staticmethod
    def generate_cache_key(*args: Any) -> str:
        """Generate a cache key from arguments"""
        combined = '_'.join(str(arg) for arg in args)
        return hashlib.md5(combined.encode()).hexdigest()

    @staticmethod
    def load_json_file(file_path: str) -> Optional[Dict]:
        """Load JSON file safely"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
        return None

    @staticmethod
    def save_json_file(file_path: str, data: Dict) -> bool:
        """Save data to JSON file safely"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving JSON file: {str(e)}")
            return False

    @staticmethod
    def is_cache_valid(cache_time: datetime, duration: int) -> bool:
        """Check if cache is still valid"""
        return datetime.now() - cache_time < timedelta(seconds=duration)

    @staticmethod
    def format_file_size(size_in_bytes: int) -> str:
        """Format file size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.2f} TB"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Limit length
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length-len(ext)] + ext
            
        return filename.strip()

    @staticmethod
    def create_directory_structure(base_dir: str, subdirs: list) -> None:
        """Create directory structure with .gitkeep files"""
        for subdir in subdirs:
            dir_path = os.path.join(base_dir, subdir)
            os.makedirs(dir_path, exist_ok=True)
            
            # Create .gitkeep file
            gitkeep_path = os.path.join(dir_path, '.gitkeep')
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    pass

    @staticmethod
    def validate_config_section(config: Dict, required_fields: list) -> tuple:
        """Validate configuration section"""
        missing = []
        invalid = []
        
        for field in required_fields:
            if field not in config:
                missing.append(field)
            elif not config[field]:
                invalid.append(field)
                
        return missing, invalid
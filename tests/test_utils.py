# tests/test_utils.py
# Version: 1.0.0
# Description: Tests for utility functions
# Changelog:
# 1.0.0 - Initial test implementation

import pytest
import os
import json
from datetime import datetime, timedelta
from src.utils.helpers import AutomationHelper
from src.utils.logger import CustomLogger

class TestAutomationHelper:
    def test_cache_key_generation(self):
        """Test cache key generation"""
        key1 = AutomationHelper.generate_cache_key("test1", "test2")
        key2 = AutomationHelper.generate_cache_key("test1", "test2")
        key3 = AutomationHelper.generate_cache_key("test2", "test1")
        
        assert key1 == key2
        assert key1 != key3

    def test_json_file_operations(self, tmp_path):
        """Test JSON file operations"""
        test_data = {"test": "data"}
        file_path = tmp_path / "test.json"
        
        # Test saving
        assert AutomationHelper.save_json_file(str(file_path), test_data)
        
        # Test loading
        loaded_data = AutomationHelper.load_json_file(str(file_path))
        assert loaded_data == test_data

    def test_cache_validation(self):
        """Test cache validation"""
        now = datetime.now()
        
        # Test valid cache
        assert AutomationHelper.is_cache_valid(now, 3600)
        
        # Test invalid cache
        old_time = now - timedelta(hours=2)
        assert not AutomationHelper.is_cache_valid(old_time, 3600)

    def test_file_size_formatting(self):
        """Test file size formatting"""
        assert AutomationHelper.format_file_size(1024) == "1.00 KB"
        assert AutomationHelper.format_file_size(1024 * 1024) == "1.00 MB"

    def test_filename_sanitization(self):
        """Test filename sanitization"""
        filename = 'test/file:name*.txt'
        sanitized = AutomationHelper.sanitize_filename(filename)
        assert '/' not in sanitized
        assert ':' not in sanitized
        assert '*' not in sanitized

class TestCustomLogger:
    @pytest.fixture
    def logger_config(self):
        """Logger configuration fixture"""
        return {
            'level': 'INFO',
            'file_path': 'logs/test.log',
            'max_size': 1024,
            'backup_count': 3
        }

    def test_logger_creation(self, logger_config):
        """Test logger creation"""
        logger = CustomLogger("test", logger_config)
        assert logger.get_logger() is not None

    def test_logger_file_creation(self, logger_config, tmp_path):
        """Test log file creation"""
        logger_config['file_path'] = str(tmp_path / "test.log")
        logger = CustomLogger("test", logger_config)
        logger.get_logger().info("Test message")
        
        assert os.path.exists(logger_config['file_path'])

if __name__ == '__main__':
    pytest.main(['-v', 'test_utils.py'])
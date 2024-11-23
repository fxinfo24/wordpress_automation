# tests/test_config_manager.py
# Version: 1.0.0
# Description: Tests for configuration management
# Changelog:
# 1.0.0 - Initial test implementation

import pytest
import os
from src.config_manager import ConfigManager

class TestConfigManager:
    @pytest.fixture
    def config_manager(self, tmp_path):
        """Create a temporary config file and manager for testing"""
        config_content = """
[wordpress]
url = http://test.com
username = test_user
password = test_pass

[openai]
api_key = test_key
model = gpt-4

[unsplash]
access_key = test_key

[images]
min_width = 1200
min_height = 800
quality = 85

[content]
min_word_count = 3200
max_retries = 3
"""
        config_file = tmp_path / "test_config.ini"
        config_file.write_text(config_content)
        return ConfigManager(str(config_file))

    def test_config_loading(self, config_manager):
        """Test configuration loading"""
        assert config_manager.get_config('wordpress', 'url') == 'http://test.com'
        assert config_manager.get_config('openai', 'model') == 'gpt-4'

    def test_missing_config(self, tmp_path):
        """Test handling of missing configuration file"""
        with pytest.raises(FileNotFoundError):
            ConfigManager(str(tmp_path / "nonexistent.ini"))

    def test_invalid_config(self, tmp_path):
        """Test handling of invalid configuration"""
        invalid_config = """
[wordpress]
url = http://test.com
# Missing required fields
"""
        config_file = tmp_path / "invalid_config.ini"
        config_file.write_text(invalid_config)
        
        with pytest.raises(ValueError):
            ConfigManager(str(config_file))

    def test_version_control(self, config_manager, tmp_path):
        """Test version control functionality"""
        config_manager.save_version_info()
        version_file = 'version_control/versions.json'
        
        assert os.path.exists(version_file)
        assert config_manager.VERSION == "1.0.0"
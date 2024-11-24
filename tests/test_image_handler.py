#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 14:31:41 2024

@author: thesaint
"""


# tests/test_image_handler.py
# Version: 1.0.0
# Description: Tests for image handling functionality
# Changelog:
# 1.0.0 - Initial test implementation

import pytest
from unittest.mock import Mock, patch
from io import BytesIO
from PIL import Image
from src.image_handler import ImageHandler
from src.config_manager import ConfigManager

class TestImageHandler:
    @pytest.fixture
    def config_manager(self):
        """Mock configuration manager"""
        config = Mock(spec=ConfigManager)
        config.get_config.return_value = 'test_key'
        config.get_section.return_value = {
            'min_width': '1200',
            'min_height': '800',
            'quality': '85'
        }
        return config

    @pytest.fixture
    def image_handler(self, config_manager):
        """Create ImageHandler instance for testing"""
        return ImageHandler(config_manager)

    def test_fetch_images(self, image_handler):
        """Test image fetching functionality"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'results': [
                    {
                        'urls': {'raw': 'test_url'},
                        'width': 1200,
                        'height': 800,
                        'description': 'test description',
                        'user': {'name': 'test user'},
                        'links': {'download_location': 'test_location'}
                    }
                ]
            }
            mock_get.return_value.raise_for_status = Mock()
            
            images = image_handler.fetch_images('test', 1)
            assert len(images) > 0
            assert 'url' in images[0]
            assert 'width' in images[0]
            assert 'height' in images[0]

    def test_process_image(self, image_handler):
        """Test image processing functionality"""
        # Create a test image
        test_image = Image.new('RGB', (1200, 800), color='red')
        img_byte_arr = BytesIO()
        test_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.content = img_byte_arr.getvalue()
            mock_get.return_value.raise_for_status = Mock()
            
            result = image_handler.process_image('test_url')
            assert result is not None
            
            # Verify the processed image
            processed_image = Image.open(result)
            assert processed_image.mode == 'RGB'
            assert processed_image.size[0] <= 1200
            assert processed_image.size[1] <= 800

    def test_cache_functionality(self, image_handler):
        """Test image caching functionality"""
        test_data = [{'url': 'test_url', 'width': 1200, 'height': 800}]
        cache_key = image_handler._generate_cache_key('test_keyword')
        
        # Test saving to cache
        image_handler._save_to_cache(cache_key, test_data)
        
        # Test retrieving from cache
        cached_data = image_handler._get_from_cache(cache_key)
        assert cached_data == test_data

if __name__ == '__main__':
    pytest.main(['-v', 'test_image_handler.py'])
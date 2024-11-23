#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 08:03:16 2024

@author: thesaint
"""

# tests/conftest.py
# Version: 1.0.0

import os
import sys
import pytest
from unittest.mock import Mock

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_config():
    """Provide mock configuration for testing"""
    return {
        'openai_api_key': 'test_openai_key',
        'wp_client': Mock(),
        'model': 'gpt-4',
        'default_word_count': 3200,
        'youtube_api_key': 'test_youtube_key'
    }

@pytest.fixture
def sample_content():
    """Provide sample content for testing"""
    return {
        'title': 'Test Article',
        'content': 'Test content\n' * 1000,
        'word_count': 3200,
        'target_word_count': 3200,
        'generated_at': '2024-01-01T00:00:00',
        'version': '1.2.0'
    }

@pytest.fixture
def sample_images():
    """Provide sample image data for testing"""
    return [
        {
            'url': 'http://test.com/image1.jpg',
            'content': b'test_image_data_1',
            'description': 'Test Image 1'
        },
        {
            'url': 'http://test.com/image2.jpg',
            'content': b'test_image_data_2',
            'description': 'Test Image 2'
        }
    ]
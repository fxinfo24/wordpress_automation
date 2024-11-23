#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 06:48:44 2024

@author: thesaint
"""

# tests/test_wordpress_manager.py
# Version: 1.0.0

import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.wordpress_manager import WordPressManager, ContentFormatter, PostVersionControl
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts

class TestWordPressManager:
    @pytest.fixture
    def wp_manager(self):
        """Create WordPressManager instance for testing"""
        with patch('wordpress_xmlrpc.Client'):
            return WordPressManager(
                'http://test.com/xmlrpc.php',
                'test_user',
                'test_pass'
            )

    @pytest.fixture
    def sample_post_data(self):
        """Sample post data for testing"""
        return {
            'title': 'Test Post',
            'content': 'Test content with multiple paragraphs.\n\n' * 3,
            'images': [
                {
                    'url': 'http://test.com/image1.jpg',
                    'description': 'Test Image 1'
                },
                {
                    'url': 'http://test.com/image2.jpg',
                    'description': 'Test Image 2'
                }
            ]
        }

    def test_initialization(self, wp_manager):
        """Test WordPress manager initialization"""
        assert isinstance(wp_manager.client, Client)
        assert wp_manager.VERSION == '1.0.0'
        assert hasattr(wp_manager, 'logger')

    def test_create_post(self, wp_manager, sample_post_data):
        """Test post creation"""
        with patch.object(wp_manager.client, 'call') as mock_call:
            mock_call.return_value = '123'  # Simulated post ID
            
            result = wp_manager.create_post(
                sample_post_data['title'],
                sample_post_data['content'],
                sample_post_data['images']
            )
            
            assert result['status'] == 'success'
            assert result['post_id'] == '123'
            assert mock_call.called
            
            # Verify the call arguments
            call_args = mock_call.call_args[0][0]
            assert isinstance(call_args, posts.NewPost)

    def test_update_post(self, wp_manager):
        """Test post update"""
        with patch.object(wp_manager.client, 'call') as mock_call:
            mock_call.return_value = True
            
            result = wp_manager.update_post(
                123,
                title='Updated Title',
                content='Updated content'
            )
            
            assert result['status'] == 'success'
            assert result['post_id'] == 123
            assert mock_call.called

    def test_error_handling(self, wp_manager, sample_post_data):
        """Test error handling"""
        with patch.object(wp_manager.client, 'call') as mock_call:
            mock_call.side_effect = Exception("Test error")
            
            result = wp_manager.create_post(
                sample_post_data['title'],
                sample_post_data['content'],
                sample_post_data['images']
            )
            
            assert result['status'] == 'error'
            assert 'message' in result

class TestContentFormatter:
    @pytest.fixture
    def formatter(self):
        """Create ContentFormatter instance"""
        return ContentFormatter()

    def test_format_content_with_images(self, formatter):
        """Test content formatting with images"""
        content = "Test content"
        images = [
            {'url': 'test1.jpg', 'description': 'Test 1'},
            {'url': 'test2.jpg', 'description': 'Test 2'}
        ]
        
        formatted_content = formatter.format_content_with_images(content, images)
        
        assert content in formatted_content
        assert 'test1.jpg' in formatted_content
        assert 'test2.jpg' in formatted_content
        assert 'Test 1' in formatted_content
        assert 'Test 2' in formatted_content

    def test_format_content_error_handling(self, formatter):
        """Test error handling in content formatting"""
        content = "Test content"
        images = None  # Invalid images data
        
        formatted_content = formatter.format_content_with_images(content, images)
        assert formatted_content == content  # Should return original content on error

class TestPostVersionControl:
    @pytest.fixture
    def version_control(self, tmp_path):
        """Create PostVersionControl instance with temporary directory"""
        with patch('os.makedirs'):
            return PostVersionControl()

    @pytest.fixture
    def sample_post_history(self):
        """Sample post history data"""
        return {
            'post_id': '123',
            'title': 'Test Post',
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }

    def test_save_and_load_history(self, version_control, sample_post_history):
        """Test saving and loading post history"""
        # Mock file operations
        mock_open = mock_open()
        with patch('builtins.open', mock_open):
            # Save post history
            version_control.save_post_history(sample_post_history)
            
            # Verify file write operation
            mock_open.assert_called()
            handle = mock_open()
            handle.write.assert_called()

    def test_load_nonexistent_history(self, version_control):
        """Test loading history when file doesn't exist"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            history = version_control._load_post_history()
            assert history == []

# Helper function for mocking file operations
def mock_open(mock=None):
    """Helper to create a mock file object"""
    if mock is None:
        mock = MagicMock()
    return mock

if __name__ == '__main__':
    pytest.main(['-v', __file__])
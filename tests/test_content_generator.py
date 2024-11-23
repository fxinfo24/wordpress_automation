#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 08:04:30 2024

@author: thesaint
"""

# tests/test_content_generator.py
# Version: 1.0.0

import pytest
from unittest.mock import patch, Mock
from src.content_generator import ContentGenerator

class TestContentGenerator:
    @pytest.fixture
    def content_generator(self, mock_config):
        """Create ContentGenerator instance for testing"""
        return ContentGenerator(mock_config)

    def test_initialization(self, content_generator):
        """Test proper initialization"""
        assert content_generator.VERSION == "1.2.0"
        assert content_generator.model == "gpt-4"
        assert content_generator.default_word_count == 3200

    def test_generate_content(self, content_generator):
        """Test content generation"""
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.return_value.choices = [
                Mock(message=Mock(content="Test Title\nTest content" * 1000))
            ]
            
            result = content_generator.generate_content(
                "Test Topic",
                ["test", "keywords"],
                word_count=1500
            )
            
            assert result['status'] != 'error'
            assert 'title' in result
            assert 'content' in result
            assert 'word_count' in result

    def test_generate_complete_post(self, content_generator, sample_images):
        """Test complete post generation with media"""
        with patch.multiple(content_generator,
                          generate_content=Mock(return_value={
                              'title': 'Test',
                              'content': 'Test content',
                              'word_count': 3200
                          }),
                          _fetch_youtube_video=Mock(return_value='https://youtube.com/test'),
                          _upload_media_to_wordpress=Mock(return_value=1)):
            
            result = content_generator.generate_complete_post(
                "Test Topic",
                ["test", "keywords"],
                word_count=3200,
                include_video=True
            )
            
            assert result['status'] == 'success'
            assert 'video_url' in result
            assert 'images' in result

    def test_word_count_validation(self, content_generator):
        """Test word count validation"""
        content = {
            'word_count': 3200,
            'target_word_count': 3200
        }
        assert content_generator._validate_word_count(content, 3200)
        
        content['word_count'] = 2000
        assert not content_generator._validate_word_count(content, 3200)

    def test_media_formatting(self, content_generator):
        """Test media formatting in content"""
        content = "Test content"
        image_ids = [1, 2, 3]
        video_url = "https://youtube.com/test"
        
        formatted = content_generator._format_content_with_media(
            content,
            image_ids,
            video_url
        )
        
        assert '[featured-image' in formatted
        assert '[gallery' in formatted
        assert '[embed]' in formatted
        assert video_url in formatted

    def test_error_handling(self, content_generator):
        """Test error handling"""
        with patch('openai.ChatCompletion.create') as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            result = content_generator.generate_content(
                "Test Topic",
                ["test", "keywords"]
            )
            
            assert result['status'] == 'error'
            assert 'message' in result

if __name__ == '__main__':
    pytest.main(['-v', __file__])
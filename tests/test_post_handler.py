# tests/test_post_handler.py
# Version: 1.0.0
# Description: Tests for WordPress post handler
# Changelog:
# 1.0.0 - Initial test implementation

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.post_handler import WordPressPostHandler
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, media

class TestWordPressPostHandler:
    @pytest.fixture
    def config_manager(self):
        """Mock configuration manager"""
        config = Mock()
        config.get_section.return_value = {
            'url': 'http://test.com',
            'xmlrpc_path': '/xmlrpc.php',
            'username': 'test_user',
            'password': 'test_pass'
        }
        return config

    @pytest.fixture
    def post_handler(self, config_manager):
        """Create WordPressPostHandler instance for testing"""
        return WordPressPostHandler(config_manager)

    @pytest.fixture
    def sample_content_data(self):
        """Sample content data for testing"""
        return {
            'title': 'Test Post',
            'content': 'Test content with multiple paragraphs.\n\n' * 5,
            'categories': ['Test Category'],
            'tags': ['test', 'sample']
        }

    @pytest.fixture
    def sample_images(self):
        """Sample image data for testing"""
        return [
            {
                'url': 'http://test.com/image1.jpg',
                'content': b'fake_image_data_1',
                'description': 'Test Image 1'
            },
            {
                'url': 'http://test.com/image2.jpg',
                'content': b'fake_image_data_2',
                'description': 'Test Image 2'
            }
        ]

    def test_initialization(self, post_handler):
        """Test post handler initialization"""
        assert isinstance(post_handler.client, Client)
        assert post_handler.VERSION == "1.0.0"

    def test_create_post_with_media(self, post_handler, sample_content_data, 
                                  sample_images):
        """Test post creation with media"""
        with patch.object(post_handler.client, 'call') as mock_call:
            # Mock media upload response
            mock_call.side_effect = [
                {'id': 1},  # First image upload
                {'id': 2},  # Second image upload
                '123'      # Post creation
            ]

            result = post_handler.create_post_with_media(
                sample_content_data,
                sample_images
            )

            assert result['status'] == 'success'
            assert result['post_id'] == '123'
            assert len(result['image_ids']) == 2

    def test_upload_media(self, post_handler, sample_images):
        """Test media upload"""
        with patch.object(post_handler.client, 'call') as mock_call:
            mock_call.return_value = {'id': 1}

            image_id = post_handler._upload_media(sample_images[0])
            
            assert image_id == 1
            assert mock_call.called
            
            # Verify the call arguments
            call_args = mock_call.call_args[0][0]
            assert isinstance(call_args, media.UploadFile)

    def test_prepare_content(self, post_handler, sample_content_data, 
                           sample_images):
        """Test content preparation with images"""
        formatted_content = post_handler._prepare_content(
            sample_content_data['content'],
            sample_images
        )

        # Verify image HTML is inserted
        assert '<figure class="wp-block-image size-large">' in formatted_content
        assert sample_images[1]['url'] in formatted_content
        assert sample_images[1]['description'] in formatted_content

    def test_update_post(self, post_handler, sample_content_data):
        """Test post update"""
        with patch.object(post_handler.client, 'call') as mock_call:
            mock_call.return_value = True

            result = post_handler.update_post(123, sample_content_data)

            assert result['status'] == 'success'
            assert result['post_id'] == 123
            assert mock_call.called
            
            # Verify the call arguments
            call_args = mock_call.call_args[0][0]
            assert isinstance(call_args, posts.EditPost)

    def test_error_handling(self, post_handler, sample_content_data):
        """Test error handling"""
        with patch.object(post_handler.client, 'call') as mock_call:
            mock_call.side_effect = Exception("Test error")

            result = post_handler.create_post_with_media(
                sample_content_data,
                []
            )

            assert result['status'] == 'error'
            assert 'message' in result

    @pytest.mark.parametrize("content,expected_count", [
        ("Test content", 0),
        ("Test content</p>Test content</p>", 1),
        ("Test content</p>" * 5, 4)
    ])
    def test_image_insertion_positions(self, post_handler, content, 
                                     expected_count):
        """Test image insertion at different positions"""
        images = [
            {'url': f'test{i}.jpg', 'description': f'test{i}'} 
            for i in range(expected_count + 1)
        ]
        
        formatted_content = post_handler._prepare_content(content, images)
        
        actual_count = formatted_content.count('<figure class="wp-block-image')
        assert actual_count == expected_count

    def test_invalid_configuration(self):
        """Test handling of invalid configuration"""
        invalid_config = Mock()
        invalid_config.get_section.return_value = {}
        
        with pytest.raises(Exception):
            WordPressPostHandler(invalid_config)

if __name__ == '__main__':
    pytest.main(['-v', 'test_post_handler.py'])
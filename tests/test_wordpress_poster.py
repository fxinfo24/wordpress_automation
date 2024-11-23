# tests/test_wordpress_poster.py
# Version: 1.0.0
# Description: Tests for WordPress posting functionality
# Changelog:
# 1.0.0 - Initial test implementation

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.wordpress_poster import WordPressPoster
from src.config_manager import ConfigManager

class TestWordPressPoster:
    @pytest.fixture
    def config_manager(self):
        """Mock configuration manager"""
        config = Mock(spec=ConfigManager)
        config.get_section.return_value = {
            'url': 'http://test.com',
            'username': 'test_user',
            'password': 'test_pass'
        }
        return config

    @pytest.fixture
    def wp_poster(self, config_manager):
        """Create WordPressPoster instance for testing"""
        return WordPressPoster(config_manager)

    def test_create_post(self, wp_poster):
        """Test post creation functionality"""
        with patch('wordpress_xmlrpc.Client') as mock_client:
            mock_client.return_value.call.return_value = '123'
            
            content_data = {
                'title': 'Test Post',
                'content': 'Test content',
                'categories': ['Test'],
                'tags': ['test']
            }
            
            images = [
                {
                    'url': 'http://test.com/image1.jpg',
                    'description': 'Test image 1'
                }
            ]
            
            result = wp_poster.create_post(content_data, images)
            
            assert result['status'] == 'success'
            assert result['post_id'] == '123'

    def test_update_post(self, wp_poster):
        """Test post update functionality"""
        with patch('wordpress_xmlrpc.Client') as mock_client:
            mock_client.return_value.call.return_value = True
            
            content_data = {
                'title': 'Updated Post',
                'content': 'Updated content'
            }
            
            result = wp_poster.update_post(123, content_data)
            
            assert result['status'] == 'success'
            assert result['post_id'] == 123

    def test_media_upload(self, wp_poster):
        """Test media upload functionality"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.content = b'test_image_data'
            mock_get.return_value.raise_for_status = Mock()
            
            with patch('wordpress_xmlrpc.Client') as mock_client:
                mock_client.return_value.call.return_value = {'id': 456}
                
                image_id = wp_poster._upload_media('http://test.com/image.jpg')
                
                assert image_id == 456

    def test_post_history(self, wp_poster):
        """Test post history tracking"""
        test_post = {
            'post_id': '123',
            'title': 'Test Post',
            'created_at': datetime.now().isoformat(),
            'status': 'published',
            'version': wp_poster.VERSION
        }
        
        wp_poster._save_post_history(test_post)
        history = wp_poster.get_post_history()
        
        assert len(history) > 0
        assert history[-1]['post_id'] == '123'
        assert history[-1]['version'] == wp_poster.VERSION

if __name__ == '__main__':
    pytest.main(['-v', 'test_wordpress_poster.py'])
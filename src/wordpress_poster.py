# src/wordpress_poster.py
# Version: 1.2.0
# Description: Handles WordPress content posting and management
# Changelog:
# 1.2.0 - Added post scheduling and media handling
# 1.1.0 - Added post tracking and version control
# 1.0.0 - Initial implementation

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.compat import xmlrpc_client
from src.config_manager import ConfigManager

class WordPressPoster:
    VERSION = "1.2.0"
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize WordPress poster with configuration"""
        self.config = config_manager
        
        # Setup WordPress client
        wp_config = self.config.get_section('wordpress')
        self.client = Client(
            f"{wp_config['url']}/xmlrpc.php",
            wp_config['username'],
            wp_config['password']
        )
        
        # Setup directories
        self.post_history_dir = 'data/post_history'
        self.media_dir = 'data/media'
        os.makedirs(self.post_history_dir, exist_ok=True)
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"WordPressPoster v{self.VERSION} initialized")
        
        # Load post history
        self.post_history = self._load_post_history()

    def create_post(self, 
                   content_data: Dict,
                   images: List[Dict],
                   schedule_time: Optional[datetime] = None) -> Dict:
        """Create a WordPress post with images and tracking"""
        try:
            # Prepare post
            post = WordPressPost()
            post.title = content_data['title']
            post.content = self._prepare_content(content_data['content'], images)
            post.post_status = 'future' if schedule_time else 'publish'
            post.terms_names = {
                'category': content_data.get('categories', ['Article']),
                'post_tag': content_data.get('tags', [])
            }
            
            if schedule_time:
                post.date = schedule_time
            
            # Upload and set featured image
            if images:
                featured_image_id = self._upload_media(images[0]['url'])
                if featured_image_id:
                    post.thumbnail = featured_image_id
            
            # Create post
            post_id = self.client.call(posts.NewPost(post))
            
            # Track post creation
            post_data = {
                'post_id': post_id,
                'title': content_data['title'],
                'created_at': datetime.now().isoformat(),
                'status': 'scheduled' if schedule_time else 'published',
                'version': self.VERSION,
                'images': [img['url'] for img in images],
                'categories': content_data.get('categories', ['Article']),
                'tags': content_data.get('tags', [])
            }
            
            self._save_post_history(post_data)
            
            self.logger.info(
                f"Successfully created post: {content_data['title']} (ID: {post_id})"
            )
            return {'status': 'success', 'post_id': post_id}

        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def update_post(self, 
                   post_id: int,
                   content_data: Dict,
                   images: Optional[List[Dict]] = None) -> Dict:
        """Update an existing WordPress post"""
        try:
            post = WordPressPost()
            post.id = post_id
            post.title = content_data.get('title')
            
            if images:
                post.content = self._prepare_content(content_data['content'], images)
            else:
                post.content = content_data['content']
            
            # Update post
            success = self.client.call(posts.EditPost(post_id, post))
            
            if success:
                # Track post update
                update_data = {
                    'post_id': post_id,
                    'title': content_data.get('title'),
                    'updated_at': datetime.now().isoformat(),
                    'version': self.VERSION,
                    'update_type': 'content_update'
                }
                
                self._save_post_history(update_data)
                
                self.logger.info(f"Successfully updated post ID: {post_id}")
                return {'status': 'success', 'post_id': post_id}
            
            return {'status': 'error', 'message': 'Update failed'}

        except Exception as e:
            self.logger.error(f"Error updating post: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _prepare_content(self, content: str, images: List[Dict]) -> str:
        """Prepare content with images and formatting"""
        try:
            # Add images to content
            formatted_content = content
            
            for i, image in enumerate(images[1:], 1):  # Skip first image (featured)
                image_id = self._upload_media(image['url'])
                if image_id:
                    image_html = f'<figure class="wp-block-image size-large">'
                    image_html += f'[caption]{image["description"]}[/caption]'
                    image_html += f'</figure>'
                    
                    # Insert image after every few paragraphs
                    insert_point = formatted_content.find('</p>', 
                                                        (len(formatted_content) // 
                                                         (len(images) - 1)) * i)
                    if insert_point != -1:
                        formatted_content = (formatted_content[:insert_point + 4] + 
                                          image_html + 
                                          formatted_content[insert_point + 4:])
            
            return formatted_content

        except Exception as e:
            self.logger.error(f"Error preparing content: {str(e)}")
            return content

    def _upload_media(self, image_url: str) -> Optional[int]:
        """Upload media to WordPress"""
        try:
            # Download image
            import requests
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Prepare image data
            file_name = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            image_data = {
                'name': file_name,
                'type': 'image/jpeg',
                'bits': xmlrpc_client.Binary(response.content)
            }
            
            # Upload to WordPress
            response = self.client.call(media.UploadFile(image_data))
            return response['id']

        except Exception as e:
            self.logger.error(f"Error uploading media: {str(e)}")
            return None

    def _load_post_history(self) -> List[Dict]:
        """Load post history from file"""
        history_file = os.path.join(
            self.post_history_dir,
            f'post_history_v{self.VERSION}.json'
        )
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading post history: {str(e)}")
        return []

    def _save_post_history(self, post_data: Dict) -> None:
        """Save post history to file"""
        try:
            self.post_history.append(post_data)
            
            history_file = os.path.join(
                self.post_history_dir,
                f'post_history_v{self.VERSION}.json'
            )
            
            with open(history_file, 'w') as f:
                json.dump(self.post_history, f, indent=4)
                
        except Exception as e:
            self.logger.error(f"Error saving post history: {str(e)}")

    def get_post_history(self) -> List[Dict]:
        """Get post history"""
        return self.post_history

    def get_version(self) -> str:
        """Get current version"""
        return self.VERSION
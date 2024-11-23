# src/post_handler.py
# Version: 1.0.0
# Description: Handles WordPress post creation and media uploads
# Changelog:
# 1.0.0 - Initial implementation

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, media
from wordpress_xmlrpc.compat import xmlrpc_client
import logging
from typing import Dict, Optional
from datetime import datetime

class WordPressPostHandler:
    VERSION = "1.0.0"
    
    def __init__(self, config_manager):
        """Initialize WordPress post handler"""
        self.config = config_manager
        wp_config = self.config.get_section('wordpress')
        
        # Initialize WordPress client
        self.client = Client(
            f"{wp_config['url']}{wp_config['xmlrpc_path']}",
            wp_config['username'],
            wp_config['password']
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"WordPressPostHandler v{self.VERSION} initialized")

    def create_post_with_media(self, 
                             content_data: Dict, 
                             images: list) -> Dict:
        """Create a WordPress post with media"""
        try:
            # First, upload images
            image_ids = []
            for image in images:
                image_id = self._upload_media(image)
                if image_id:
                    image_ids.append(image_id)

            # Create post
            post = WordPressPost()
            post.title = content_data['title']
            post.content = self._prepare_content(content_data['content'], images)
            post.post_status = 'publish'
            post.terms_names = {
                'category': content_data.get('categories', ['Article']),
                'post_tag': content_data.get('tags', [])
            }

            # Set featured image if available
            if image_ids:
                post.thumbnail = image_ids[0]

            # Create the post
            post_id = self.client.call(posts.NewPost(post))

            self.logger.info(f"Successfully created post: {post_id}")
            return {
                'status': 'success',
                'post_id': post_id,
                'image_ids': image_ids
            }

        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _upload_media(self, image_data: Dict) -> Optional[int]:
        """Upload media to WordPress"""
        try:
            # Prepare media data
            data = {
                'name': f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                'type': 'image/jpeg',
                'bits': xmlrpc_client.Binary(image_data['content'])
            }

            # Upload file
            response = self.client.call(media.UploadFile(data))
            
            if response and 'id' in response:
                self.logger.info(f"Successfully uploaded media: {response['id']}")
                return response['id']
            
            return None

        except Exception as e:
            self.logger.error(f"Error uploading media: {str(e)}")
            return None

    def _prepare_content(self, content: str, images: list) -> str:
        """Prepare content with images"""
        try:
            formatted_content = content

            # Insert additional images throughout the content
            for i, image in enumerate(images[1:], 1):  # Skip first image (featured)
                image_html = (
                    f'<figure class="wp-block-image size-large">'
                    f'<img src="{image["url"]}" alt="{image.get("description", "")}">'
                    f'</figure>'
                )
                
                # Insert image after every few paragraphs
                insert_point = formatted_content.find(
                    '</p>', 
                    (len(formatted_content) // (len(images))) * i
                )
                
                if insert_point != -1:
                    formatted_content = (
                        formatted_content[:insert_point + 4] + 
                        image_html + 
                        formatted_content[insert_point + 4:]
                    )

            return formatted_content

        except Exception as e:
            self.logger.error(f"Error preparing content: {str(e)}")
            return content

    def update_post(self, post_id: int, content_data: Dict) -> Dict:
        """Update an existing post"""
        try:
            post = WordPressPost()
            post.id = post_id
            
            if 'title' in content_data:
                post.title = content_data['title']
            if 'content' in content_data:
                post.content = content_data['content']
            if 'status' in content_data:
                post.post_status = content_data['status']

            success = self.client.call(posts.EditPost(post_id, post))
            
            if success:
                self.logger.info(f"Successfully updated post: {post_id}")
                return {'status': 'success', 'post_id': post_id}
            
            return {
                'status': 'error',
                'message': 'Failed to update post'
            }

        except Exception as e:
            self.logger.error(f"Error updating post: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
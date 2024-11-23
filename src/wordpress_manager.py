#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 06:40:11 2024

@author: thesaint
"""

# src/wordpress_manager.py
# Version: 1.0.0

import os
import json
import logging
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts, media

class WordPressManager:
    VERSION = '1.0.0'

    def __init__(self, wp_url: str, username: str, password: str):
        """Initialize WordPress manager with credentials"""
        self.client = Client(wp_url, username, password)
        self.logger = self._setup_logging()
        self.content_formatter = ContentFormatter()
        self.version_control = PostVersionControl()
        
        self.logger.info(f"WordPressManager v{self.VERSION} initialized")

    def _setup_logging(self):
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename='logs/wordpress_manager.log',
            level=logging.DEBUG,
            format='%(asctime)s - v%(version)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return logging.getLogger(self.__class__.__name__)

    def create_post(self, title: str, content: str, images: list) -> dict:
        """Create WordPress post with images"""
        try:
            # Format content with images
            formatted_content = self.content_formatter.format_content_with_images(
                content, 
                images
            )

            # Create post
            post = WordPressPost()
            post.title = title
            post.content = formatted_content
            post.post_status = 'publish'

            # Create the post
            post_id = self.client.call(posts.NewPost(post))

            # Track post creation
            post_data = {
                'post_id': post_id,
                'title': title,
                'created_at': datetime.now().isoformat(),
                'version': self.VERSION
            }
            self.version_control.save_post_history(post_data)

            self.logger.info(f"Successfully created post: {post_id}")
            return {'status': 'success', 'post_id': post_id}

        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def update_post(self, post_id: int, title: str = None, 
                   content: str = None) -> dict:
        """Update existing post"""
        try:
            post = WordPressPost()
            post.id = post_id
            if title:
                post.title = title
            if content:
                post.content = content

            success = self.client.call(posts.EditPost(post_id, post))
            
            if success:
                update_data = {
                    'post_id': post_id,
                    'updated_at': datetime.now().isoformat(),
                    'version': self.VERSION
                }
                self.version_control.save_post_history(update_data)
                
                self.logger.info(f"Successfully updated post: {post_id}")
                return {'status': 'success', 'post_id': post_id}
            
            return {'status': 'error', 'message': 'Update failed'}

        except Exception as e:
            self.logger.error(f"Error updating post: {str(e)}")
            return {'status': 'error', 'message': str(e)}

class ContentFormatter:
    VERSION = '1.0.0'

    def format_content_with_images(self, content: str, images: list) -> str:
        """Format content with embedded images"""
        try:
            formatted_content = content
            image_html_template = '<img src="{}" alt="{}" />'
            for image in images:
                image_html = image_html_template.format(
                    image['url'], 
                    image.get('description', '')
                )
                formatted_content += image_html

            return formatted_content
        except Exception as e:
            logging.error(f'Error formatting content: {str(e)}')
            return content

class PostVersionControl:
    VERSION = '1.0.0'
 
    def __init__(self):
        """Initialize version control"""
        self.history_file = f'version_control/post_history_v{self.VERSION}.json'
        os.makedirs('version_control', exist_ok=True)
        self.post_history = self._load_post_history()

    def _load_post_history(self):
        """Load post history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f'Error loading post history: {str(e)}')
        return []

    def save_post_history(self, post_data):
        """Save post history to file"""
        self.post_history.append(post_data)
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.post_history, f, indent=4)
        except Exception as e:
            print(f'Error saving post history: {str(e)}')
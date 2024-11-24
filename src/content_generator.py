#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 14:31:41 2024

@author: thesaint
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 07:50:59 2024

@author: thesaint
"""

# src/content_generator.py
# Version: 1.2.0
# Description: Handles content generation with OpenAI API, media handling, and word count control
# Changelog:
# 1.2.0 - Added media handling with WordPress XML-RPC API
# 1.1.0 - Added flexible word count control
# 1.0.0 - Initial implementation

import os
import openai
import logging
import requests
from typing import Dict, Optional, List, Union
from datetime import datetime
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client

class ContentGenerator:
    VERSION = "1.2.0"
    
    def __init__(self, config: Dict):
        """
        Initialize ContentGenerator with configuration
        
        Args:
            config (Dict): Configuration dictionary containing:
                - openai_api_key: OpenAI API key
                - wp_client: WordPress XML-RPC client
                - model: OpenAI model to use
                - default_word_count: Default word count for articles
                - youtube_api_key: YouTube Data API key
        """
        self.openai_api_key = config['openai_api_key']
        self.wp_client = config['wp_client']
        self.model = config.get('model', 'gpt-4')
        self.default_word_count = config.get('default_word_count', 3200)
        self.youtube_api_key = config.get('youtube_api_key')
        
        openai.api_key = self.openai_api_key
        
        # Setup logging
        self.logger = self._setup_logging()
        self.logger.info(f"ContentGenerator v{self.VERSION} initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename=f'logs/content_generator_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - v%(version)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def generate_complete_post(self,
                             topic: str,
                             keywords: list,
                             word_count: Optional[int] = None,
                             outline: Optional[Dict] = None,
                             include_video: bool = True) -> Dict:
        """
        Generate complete post with content and media
        
        Args:
            topic (str): Main topic of the article
            keywords (list): List of keywords to include
            word_count (int, optional): Desired word count
            outline (Dict, optional): Custom outline
            include_video (bool): Whether to include YouTube video
        """
        try:
            # Generate content
            content_result = self.generate_content(topic, keywords, word_count, outline)
            if content_result.get('status') == 'error':
                return content_result

            # Fetch and process images
            images = self._fetch_images(topic, keywords)
            
            # Fetch relevant video if requested
            video_url = None
            if include_video:
                video_url = self._fetch_youtube_video(topic, keywords)

            # Combine content with media
            final_content = self.generate_content_with_media(
                content_result['content'],
                images,
                video_url
            )

            return {
                'status': 'success',
                'title': content_result['title'],
                'content': final_content,
                'word_count': content_result['word_count'],
                'images': images,
                'video_url': video_url,
                'generated_at': datetime.now().isoformat(),
                'version': self.VERSION
            }

        except Exception as e:
            self.logger.error(f"Error generating complete post: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def generate_content(self, 
                        topic: str,
                        keywords: list,
                        word_count: Optional[int] = None,
                        outline: Optional[Dict] = None) -> Dict:
        """Generate article content using OpenAI API"""
        try:
            target_word_count = word_count or self.default_word_count
            prompt = self._create_prompt(topic, keywords, target_word_count, outline)
            max_tokens = self._calculate_tokens(target_word_count)
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            processed_content = self._process_content(content, target_word_count)
            
            if not self._validate_word_count(processed_content, target_word_count):
                self.logger.warning("Content length doesn't match target. Regenerating...")
                return self.generate_content(topic, keywords, word_count, outline)
            
            return processed_content

        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def generate_content_with_media(self, 
                                  content: str, 
                                  images: List[Dict],
                                  video_url: Optional[str] = None) -> str:
        """Format content with media elements"""
        try:
            formatted_content = content

            # Handle images
            if images:
                # Upload images to WordPress
                image_ids = []
                for image in images:
                    image_id = self._upload_media_to_wordpress(image)
                    if image_id:
                        image_ids.append(image_id)

                # Format content with images
                formatted_content = self._format_content_with_media(
                    formatted_content,
                    image_ids,
                    video_url
                )

            return formatted_content

        except Exception as e:
            self.logger.error(f"Error formatting content with media: {str(e)}")
            return content

    def _create_prompt(self, 
                      topic: str, 
                      keywords: list, 
                      word_count: int,
                      outline: Optional[Dict] = None) -> str:
        """Create detailed prompt for content generation"""
        prompt = f"""
Write a comprehensive article about: {topic}

Key Requirements:
- Article length: Exactly {word_count} words
- Include these keywords naturally: {', '.join(keywords)}
- Write in a professional, engaging tone
- Include relevant examples and data
- Optimize for SEO while maintaining readability

Content Distribution:
- Introduction: ~{int(word_count * 0.1)} words
- Main content: ~{int(word_count * 0.7)} words
- Examples and data: ~{int(word_count * 0.1)} words
- Conclusion: ~{int(word_count * 0.1)} words

Structure:
1. Engaging introduction with hook
2. Main content sections with subheadings
3. Practical examples and case studies
4. Expert insights and statistics
5. Strong conclusion with key takeaways
"""

        if outline:
            prompt += "\nCustom Outline:\n"
            for section in outline['sections']:
                prompt += f"\n{section['title']}\n"
                for subsection in section.get('subsections', []):
                    prompt += f"- {subsection}\n"

        return prompt

    def _calculate_tokens(self, word_count: int) -> int:
        """Calculate appropriate max_tokens based on desired word count"""
        return int(word_count * 1.3)

    def _process_content(self, content: str, target_word_count: int) -> Dict:
        """Process and structure the generated content"""
        try:
            lines = content.split('\n')
            title = lines[0].strip('#').strip()
            word_count = len(content.split())
            
            return {
                'title': title,
                'content': content,
                'word_count': word_count,
                'target_word_count': target_word_count,
                'generated_at': datetime.now().isoformat(),
                'version': self.VERSION
            }

        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _validate_word_count(self, content: Dict, target_word_count: int) -> bool:
        """Validate if content meets word count requirements"""
        actual_count = content['word_count']
        margin = target_word_count * 0.05  # 5% margin of error
        return abs(actual_count - target_word_count) <= margin

    def _upload_media_to_wordpress(self, image_data: Dict) -> Optional[int]:
        """Upload media to WordPress"""
        try:
            data = {
                'name': f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                'type': 'image/jpeg',
                'bits': xmlrpc_client.Binary(image_data['content'])
            }

            response = self.wp_client.call(media.UploadFile(data))
            return response.get('id')

        except Exception as e:
            self.logger.error(f"Error uploading media: {str(e)}")
            return None

    def _fetch_youtube_video(self, topic: str, keywords: list) -> Optional[str]:
        """Fetch relevant YouTube video"""
        if not self.youtube_api_key:
            return None

        try:
            search_query = f"{topic} {' '.join(keywords[:2])}"
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query,
                'key': self.youtube_api_key,
                'maxResults': 1,
                'type': 'video'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data['items']:
                video_id = data['items'][0]['id']['videoId']
                return f"https://www.youtube.com/embed/{video_id}"

            return None

        except Exception as e:
            self.logger.error(f"Error fetching YouTube video: {str(e)}")
            return None

    def _format_content_with_media(self, 
                                 content: str, 
                                 image_ids: List[int],
                                 video_url: Optional[str] = None) -> str:
        """Format content with embedded media"""
        try:
            formatted_content = content

            # Handle images
            if image_ids:
                # Set featured image
                formatted_content = f'[featured-image id="{image_ids[0]}"]\n' + formatted_content

                # Insert additional images
                for i, img_id in enumerate(image_ids[1:], 1):
                    insert_point = len(formatted_content) // (len(image_ids))
                    image_html = f'\n[gallery ids="{img_id}"]\n'
                    formatted_content = (
                        formatted_content[:insert_point] + 
                        image_html + 
                        formatted_content[insert_point:]
                    )

            # Handle video
            if video_url:
                video_embed = f'\n[embed]{video_url}[/embed]\n'
                insert_point = len(formatted_content) // 2
                formatted_content = (
                    formatted_content[:insert_point] + 
                    video_embed + 
                    formatted_content[insert_point:]
                )

            return formatted_content

        except Exception as e:
            self.logger.error(f"Error formatting content with media: {str(e)}")
            return content

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 14:31:41 2024

@author: thesaint
"""

# src/automation_manager.py
# Version: 1.0.0
# Description: Main automation manager that coordinates all components
# Changelog:
# 1.0.0 - Initial implementation

import os
import time
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.config_manager import ConfigManager
from src.image_handler import ImageHandler
from src.content_generator import ContentGenerator
from src.wordpress_poster import WordPressPoster

class AutomationManager:
    VERSION = "1.0.0"
    
    def __init__(self, config_file: str = 'config/config.ini'):
        """Initialize automation manager"""
        # Setup configuration
        self.config_manager = ConfigManager(config_file)
        
        # Initialize components
        self.image_handler = ImageHandler(self.config_manager)
        self.content_generator = ContentGenerator(self.config_manager)
        self.wp_poster = WordPressPoster(self.config_manager)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"AutomationManager v{self.VERSION} initialized")
        
        # Load posting interval from config
        self.posting_interval = int(
            self.config_manager.get_config('content', 'posting_interval')
        )

    def process_topic(self, topic_data: Dict) -> Dict:
        """Process a single topic"""
        try:
            self.logger.info(f"Processing topic: {topic_data['topic']}")
            
            # Generate content
            content = self.content_generator.generate_content(
                topic=topic_data['topic'],
                primary_keywords=topic_data['primary_keywords'],
                additional_keywords=topic_data['additional_keywords'],
                target_audience=topic_data['target_audience'],
                tone_style=topic_data['tone_style'],
                outline=topic_data.get('custom_outline')
            )
            
            if not content:
                raise ValueError("Content generation failed")

            # Fetch images
            images = self.image_handler.fetch_images(
                topic_data['primary_keywords'],
                num_images=4  # 1 featured + 3 in-content images
            )
            
            if not images:
                raise ValueError("Image fetching failed")

            # Create post
            post_result = self.wp_poster.create_post(
                content_data={
                    'title': content['title'],
                    'content': content['content'],
                    'categories': topic_data.get('categories', ['Article']),
                    'tags': topic_data['primary_keywords'].split(',')
                },
                images=images
            )
            
            return {
                'status': 'success',
                'post_id': post_result['post_id'],
                'title': content['title']
            }

        except Exception as e:
            self.logger.error(f"Error processing topic: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def run_automation(self, input_file: str) -> None:
        """Run the automation process"""
        try:
            # Load topics from file
            topics = self._load_topics(input_file)
            
            if not topics:
                raise ValueError(f"No topics found in {input_file}")

            self.logger.info(f"Starting automation with {len(topics)} topics")
            
            # Process each topic
            for index, topic in enumerate(topics, 1):
                self.logger.info(f"Processing topic {index}/{len(topics)}")
                
                # Process topic
                result = self.process_topic(topic)
                
                # Log result
                if result['status'] == 'success':
                    self.logger.info(
                        f"Successfully created post: {result['title']} "
                        f"(ID: {result['post_id']})"
                    )
                else:
                    self.logger.error(
                        f"Failed to process topic: {result['message']}"
                    )
                
                # Wait before next post
                if index < len(topics):
                    self.logger.info(
                        f"Waiting {self.posting_interval} seconds before next post"
                    )
                    time.sleep(self.posting_interval)

        except Exception as e:
            self.logger.error(f"Error in automation: {str(e)}")
            raise

    def _load_topics(self, input_file: str) -> List[Dict]:
        """Load topics from input file"""
        try:
            file_extension = os.path.splitext(input_file)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(input_file)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(input_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Convert DataFrame to list of dictionaries
            topics = df.to_dict('records')
            
            # Validate topics
            for topic in topics:
                self._validate_topic(topic)
            
            return topics

        except Exception as e:
            self.logger.error(f"Error loading topics: {str(e)}")
            raise

    def _validate_topic(self, topic: Dict) -> None:
        """Validate topic data"""
        required_fields = [
            'topic',
            'primary_keywords',
            'additional_keywords',
            'target_audience',
            'tone_style'
        ]
        
        missing_fields = [
            field for field in required_fields 
            if field not in topic or not topic[field]
        ]
        
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
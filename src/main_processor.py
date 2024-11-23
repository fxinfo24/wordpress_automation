#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 08:52:05 2024

@author: thesaint
"""

# src/main_processor.py
# Version: 1.0.0
# Description: Main processing script for content generation

import os
import logging
from typing import Dict, List
from datetime import datetime
from .utils.data_loader import DataLoader
from .content_generator import ContentGenerator

class ContentProcessor:
    VERSION = "1.0.0"

    def __init__(self, config: Dict):
        """Initialize content processor with configuration"""
        self.config = config
        self.content_generator = ContentGenerator(config)
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename=f'logs/processor_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - v%(version)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def process_topics(self, input_file: str) -> List[Dict]:
        """Process all topics from input file"""
        try:
            # Load topics
            topics = DataLoader.load_topics(input_file)
            results = []

            for topic in topics:
                self.logger.info(f"Processing topic: {topic['topic']}")
                
                try:
                    result = self.content_generator.generate_complete_post(
                        topic=topic['topic'],
                        keywords=topic['primary_keywords'].split(','),
                        word_count=topic.get('word_count', 3200),
                        outline=topic.get('custom_outline'),
                        include_video=topic.get('video_required', False)
                    )
                    results.append(result)
                    
                except Exception as e:
                    self.logger.error(f"Error processing topic '{topic['topic']}': {str(e)}")
                    results.append({
                        'status': 'error',
                        'topic': topic['topic'],
                        'message': str(e)
                    })

            return results

        except Exception as e:
            self.logger.error(f"Error processing topics: {str(e)}")
            raise

def main():
    """Main execution function"""
    # Load configuration
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'wp_client': None,  # Initialize WordPress client here
        'model': 'gpt-4',
        'default_word_count': 3200,
        'youtube_api_key': os.getenv('YOUTUBE_API_KEY')
    }

    # Initialize processor
    processor = ContentProcessor(config)

    # Process topics
    input_file = 'data/input/topics.csv'  # or 'data/input/topics.xlsx'
    results = processor.process_topics(input_file)

    # Log results
    for result in results:
        if result['status'] == 'success':
            print(f"Successfully processed: {result['title']}")
        else:
            print(f"Error processing: {result['message']}")

if __name__ == "__main__":
    main()
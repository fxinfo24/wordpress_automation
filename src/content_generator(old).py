#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 14:31:41 2024

@author: thesaint
"""

# src/content_generator.py
# Version: 1.1.0
# Description: Handles content generation using OpenAI GPT
# Changelog:
# 1.1.0 - Added content optimization and caching
# 1.0.0 - Initial implementation

import os
import json
import openai
import logging
import hashlib
from typing import Dict, Optional, List
from datetime import datetime
from src.config_manager import ConfigManager

class ContentGenerator:
    VERSION = "1.1.0"
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize ContentGenerator with configuration"""
        self.config = config_manager
        self.openai_key = self.config.get_config('openai', 'api_key')
        self.model = self.config.get_config('openai', 'model')
        openai.api_key = self.openai_key
        
        # Get content configuration
        self.content_config = self.config.get_section('content')
        self.min_words = int(self.content_config['min_word_count'])
        self.max_retries = int(self.content_config['max_retries'])
        
        # Setup cache directory
        self.cache_dir = 'data/content_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ContentGenerator v{self.VERSION} initialized")

    def _create_article_prompt(self, 
                             topic: str,
                             primary_keywords: str,
                             additional_keywords: str,
                             target_audience: str,
                             tone_style: str,
                             outline: Optional[Dict] = None) -> str:
        """Create a detailed prompt for article generation"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"""
Write a unique, original article in English on the topic: "{topic}"

Key Requirements:
- Primary Keywords: {primary_keywords}
- Additional Keywords to use naturally {additional_keywords} (20-30 times)
- Target Audience: {target_audience}
- Tone and Style: {tone_style}
- Current Date: {current_date}
- Minimum Length: {self.min_words} words

Content Structure:
1. Title (SEO-optimized, engaging)
2. Meta Description (155-160 characters)
3. Introduction
   - Hook statement
   - Context setting
   - Article overview
4. Main Content Sections
   - Detailed explanations
   - Examples and case studies
   - Statistical data where relevant
5. Practical Applications
   - Step-by-step guides
   - Best practices
   - Common pitfalls to avoid
6. FAQ Section (5 most relevant questions)
7. Conclusion
   - Key takeaways
   - Call to action

Writing Guidelines:
- Maintain a natural, conversational tone
- Use transition words for flow
- Include real-world examples
- Break down complex concepts
- Use bullet points and lists where appropriate
- Ensure proper heading hierarchy (H2, H3, H4)
"""

        if outline:
            prompt += "\nCustom Outline Structure:\n"
            for section in outline['sections']:
                prompt += f"\n{section['type'].upper()}:\n"
                for element in section['elements']:
                    prompt += f"- {element.replace('_', ' ').title()}\n"

        return prompt

    def generate_content(self,
                        topic: str,
                        primary_keywords: str,
                        additional_keywords: str,
                        target_audience: str,
                        tone_style: str,
                        outline: Optional[Dict] = None) -> Optional[Dict]:
        """Generate article content using OpenAI"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(
                topic, primary_keywords, additional_keywords
            )
            cached_content = self._get_from_cache(cache_key)
            if cached_content:
                self.logger.info(f"Retrieved content from cache for topic: {topic}")
                return cached_content

            prompt = self._create_article_prompt(
                topic,
                primary_keywords,
                additional_keywords,
                target_audience,
                tone_style,
                outline
            )

            for attempt in range(self.max_retries):
                try:
                    self.logger.info(
                        f"Generating content for topic: {topic} (Attempt {attempt + 1})"
                    )
                    
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a professional content writer with expertise in SEO and engaging writing."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=4000
                    )
                    
                    content = response.choices[0].message.content
                    
                    # Validate content
                    if not self._validate_content(content):
                        continue
                    
                    # Process and structure content
                    processed_content = self._process_content(content)
                    
                    # Cache the content
                    self._save_to_cache(cache_key, processed_content)
                    
                    self.logger.info(f"Successfully generated content for topic: {topic}")
                    return processed_content

                except Exception as e:
                    self.logger.error(
                        f"Error in attempt {attempt + 1}: {str(e)}"
                    )
                    if attempt == self.max_retries - 1:
                        raise

            return None

        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            return None

    def _validate_content(self, content: str) -> bool:
        """Validate generated content"""
        try:
            # Check word count
            word_count = len(content.split())
            if word_count < self.min_words:
                self.logger.warning(
                    f"Content too short: {word_count} words (minimum: {self.min_words})"
                )
                return False

            # Check for required sections
            required_sections = ['Introduction', 'Conclusion', 'FAQ']
            for section in required_sections:
                if section.lower() not in content.lower():
                    self.logger.warning(f"Missing required section: {section}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating content: {str(e)}")
            return False

    def _process_content(self, content: str) -> Dict:
        """Process and structure the generated content"""
        try:
            # Extract title and meta description
            lines = content.split('\n')
            title = lines[0].strip('#').strip()
            meta_desc = ''
            
            for line in lines:
                if 'Meta Description:' in line:
                    meta_desc = line.replace('Meta Description:', '').strip()
                    break

            # Structure the content
            structured_content = {
                'title': title,
                'meta_description': meta_desc,
                'content': content,
                'word_count': len(content.split()),
                'generated_at': datetime.now().isoformat(),
                'version': self.VERSION
            }

            return structured_content

        except Exception as e:
            self.logger.error(f"Error processing content: {str(e)}")
            return {
                'content': content,
                'generated_at': datetime.now().isoformat(),
                'version': self.VERSION
            }

    def _generate_cache_key(self, *args) -> str:
        """Generate a cache key from arguments"""
        combined = '_'.join(str(arg) for arg in args)
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Retrieve content from cache"""
        cache_file = os.path.join(self.cache_dir, f'{cache_key}.json')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading from cache: {str(e)}")
        return None

    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save content to cache"""
        cache_file = os.path.join(self.cache_dir, f'{cache_key}.json')
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving to cache: {str(e)}")
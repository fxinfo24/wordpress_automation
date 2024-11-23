# src/image_handler.py
# Version: 1.1.0
# Description: Handles image fetching, processing, and optimization
# Changelog:
# 1.1.0 - Added image optimization and caching
# 1.0.0 - Initial implementation

import os
import hashlib
import requests
import logging
from PIL import Image
from io import BytesIO
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ratelimit import limits, sleep_and_retry
from src.config_manager import ConfigManager

class ImageHandler:
    VERSION = "1.1.0"
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize ImageHandler with configuration"""
        self.config = config_manager
        self.unsplash_key = self.config.get_config('unsplash', 'access_key')
        self.headers = {'Authorization': f'Client-ID {self.unsplash_key}'}
        
        # Setup image specifications
        self.image_config = self.config.get_section('images')
        self.min_width = int(self.image_config['min_width'])
        self.min_height = int(self.image_config['min_height'])
        self.quality = int(self.image_config['quality'])
        
        # Setup cache directory
        self.cache_dir = 'data/image_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ImageHandler v{self.VERSION} initialized")

    @sleep_and_retry
    @limits(calls=30, period=60)  # Unsplash API rate limit
    def fetch_images(self, keyword: str, num_images: int = 4) -> List[Dict]:
        """
        Fetch images from Unsplash with rate limiting and caching
        """
        try:
            cache_key = self._generate_cache_key(keyword, num_images)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                self.logger.info(f"Retrieved {len(cached_result)} images from cache")
                return cached_result

            self.logger.info(f"Fetching {num_images} images for keyword: {keyword}")
            
            response = requests.get(
                'https://api.unsplash.com/search/photos',
                params={
                    'query': keyword,
                    'per_page': num_images * 2,  # Fetch extra for backup
                    'orientation': 'landscape'
                },
                headers=self.headers
            )
            response.raise_for_status()
            
            images = []
            for photo in response.json()['results']:
                if len(images) >= num_images:
                    break
                    
                if (photo['width'] >= self.min_width and 
                    photo['height'] >= self.min_height):
                    images.append({
                        'url': photo['urls']['raw'],
                        'width': photo['width'],
                        'height': photo['height'],
                        'description': photo['description'] or keyword,
                        'attribution': photo['user']['name'],
                        'download_location': photo['links']['download_location']
                    })
            
            # Cache the results
            self._save_to_cache(cache_key, images)
            
            self.logger.info(f"Successfully fetched {len(images)} images")
            return images

        except Exception as e:
            self.logger.error(f"Error fetching images: {str(e)}")
            return []

    def process_image(self, 
                     image_url: str, 
                     target_size: Optional[Tuple[int, int]] = None) -> Optional[BytesIO]:
        """
        Process and optimize images
        """
        try:
            self.logger.info(f"Processing image from URL: {image_url}")
            
            # Try to get from cache first
            cache_key = self._generate_cache_key(image_url)
            cached_image = self._get_processed_image_from_cache(cache_key)
            if cached_image:
                return cached_image

            response = requests.get(image_url)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, 'white')
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Resize if target size is specified
            if target_size:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Optimize image
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, 
                    format='JPEG', 
                    quality=self.quality, 
                    optimize=True)
            img_byte_arr.seek(0)
            
            # Cache processed image
            self._save_processed_image_to_cache(cache_key, img_byte_arr)
            
            self.logger.info("Image processed successfully")
            return img_byte_arr

        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return None

    def _generate_cache_key(self, *args) -> str:
        """Generate a cache key from arguments"""
        combined = '_'.join(str(arg) for arg in args)
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """Retrieve images from cache"""
        cache_file = os.path.join(self.cache_dir, f'{cache_key}.json')
        try:
            if os.path.exists(cache_file):
                import json
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading from cache: {str(e)}")
        return None

    def _save_to_cache(self, cache_key: str, data: List[Dict]) -> None:
        """Save images to cache"""
        cache_file = os.path.join(self.cache_dir, f'{cache_key}.json')
        try:
            import json
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error saving to cache: {str(e)}")

    def _get_processed_image_from_cache(self, cache_key: str) -> Optional[BytesIO]:
        """Retrieve processed image from cache"""
        cache_file = os.path.join(self.cache_dir, f'{cache_key}.jpg')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    return BytesIO(f.read())
        except Exception as e:
            self.logger.error(f"Error reading processed image from cache: {str(e)}")
        return None

    def _save_processed_image_to_cache(self, cache_key: str, 
                                     image_data: BytesIO) -> None:
        """Save processed image to cache"""
        cache_file = os.path.join(self.cache_dir, f'{cache_key}.jpg')
        try:
            with open(cache_file, 'wb') as f:
                f.write(image_data.getvalue())
        except Exception as e:
            self.logger.error(f"Error saving processed image to cache: {str(e)}")
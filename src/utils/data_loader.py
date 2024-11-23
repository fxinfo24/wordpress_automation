#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 08:49:38 2024

@author: thesaint
"""

# src/utils/data_loader.py
# Version: 1.0.0
# Description: Utilities for loading and preparing input data

import pandas as pd
import json
import os
from typing import Dict, List

class DataLoader:
    VERSION = "1.0.0"

    @staticmethod
    def create_sample_data(output_path: str = 'data/input/') -> None:
        """Create sample Excel and CSV files with template data"""
        # Create sample data
        data = {
            'topic': [
                'Benefits of Organic Gardening',
                'Quick SEO Guide 2024'
            ],
            'primary_keywords': [
                'organic gardening, natural farming',
                'SEO, search optimization'
            ],
            'additional_keywords': [
                'sustainable gardening, eco-friendly, organic soil',
                'digital marketing, website ranking'
            ],
            'target_audience': [
                'home gardeners',
                'business owners'
            ],
            'tone_style': [
                'friendly, informative',
                'professional, concise'
            ],
            'word_count': [
                3200,
                1500
            ],
            'categories': [
                'Gardening,Sustainability',
                'Digital Marketing,SEO'
            ],
            'custom_outline': [
                '{"sections":[{"title":"Introduction","subsections":["What is Organic Gardening","Benefits Overview"]}]}',
                '{"sections":[{"title":"SEO Basics","subsections":["What is SEO","Why it Matters"]}]}'
            ],
            'image_keywords': [
                'organic garden, vegetables growing',
                'SEO optimization, digital marketing'
            ],
            'video_required': [
                True,
                False
            ]
        }

        # Create directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Create DataFrame
        df = pd.DataFrame(data)

        # Save to Excel
        excel_path = os.path.join(output_path, 'topics.xlsx')
        df.to_excel(excel_path, index=False)
        print(f"Created sample Excel file: {excel_path}")

        # Save to CSV
        csv_path = os.path.join(output_path, 'topics.csv')
        df.to_csv(csv_path, index=False)
        print(f"Created sample CSV file: {csv_path}")

    @staticmethod
    def load_topics(file_path: str) -> List[Dict]:
        """
        Load topics from CSV or Excel file
        
        Args:
            file_path (str): Path to the input file
            
        Returns:
            List[Dict]: List of topic dictionaries
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or Excel.")

        # Convert DataFrame to list of dictionaries
        topics = []
        for _, row in df.iterrows():
            topic_dict = row.to_dict()
            
            # Convert string representations to proper types
            if 'custom_outline' in topic_dict and topic_dict['custom_outline']:
                topic_dict['custom_outline'] = json.loads(topic_dict['custom_outline'])
            
            if 'word_count' in topic_dict:
                topic_dict['word_count'] = int(topic_dict['word_count'])
            
            if 'video_required' in topic_dict:
                topic_dict['video_required'] = bool(topic_dict['video_required'])

            topics.append(topic_dict)

        return topics

if __name__ == "__main__":
    # Create sample files when run directly
    DataLoader.create_sample_data()
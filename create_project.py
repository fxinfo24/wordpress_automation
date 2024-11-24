#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 14:31:41 2024

@author: thesaint
"""


# create_project.py
import os

def create_project_structure():
    """Create the initial project structure"""
    # Define all directories to create
    directories = [
        'src',
        'tests',
        'config',
        'data',
        'data/content_cache',
        'data/image_cache',
        'data/post_history',
        'data/media',
        'logs',
        'version_control',
        '.vscode'
    ]
    
    # Create directories and __init__.py files
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        if directory not in ['.vscode', 'logs', 'version_control']:
            with open(os.path.join(directory, '__init__.py'), 'w') as f:
                pass

    # Create .gitkeep files
    gitkeep_dirs = [
        'logs',
        'version_control',
        'data/content_cache',
        'data/image_cache',
        'data/post_history',
        'data/media'
    ]
    for directory in gitkeep_dirs:
        with open(os.path.join(directory, '.gitkeep'), 'w') as f:
            pass

    print("Project structure created successfully!")

if __name__ == "__main__":
    create_project_structure()
# create_files.py

# Create requirements.txt and README.md files
requirements_content = """# Project dependencies

python-wordpress-xmlrpc>=2.3.0
requests>=2.31.0
Pillow>=10.1.0
google-api-python-client>=2.108.0
pandas>=2.1.3
openai>=1.3.5
python-dotenv>=1.0.0
pytest>=7.4.3
ratelimit>=2.2.1
configparser>=6.0.0
"""

# Create requirements.txt
with open('requirements.txt', 'w') as f:
    f.write(requirements_content)

readme_content = """ WordPress Content Automation Tool

Version: 1.0.0

## Description
Automated content generation and posting system for WordPress blogs.

## Features
- Automated content generation using OpenAI GPT
- Image handling with Unsplash integration
- WordPress post automation
- Version control and tracking
- Comprehensive logging
- Configurable posting schedule

## Installation
1. Clone the repository:
```bash
git clone https://github.com/fxinfo24/wordpress_automation.git
cd wordpress_automation """
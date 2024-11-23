# WordPress Content Automation Tool

Version: 1.0.0

## Description

This tool automates content creation and posting for WordPress websites, featuring:

- Automated content generation using OpenAI GPT
- Intelligent image selection from Unsplash
- YouTube video integration
- WordPress post automation
- Flexible word count control
- Custom outline support
- Bulk content processing

## Features

1. Content Generation:

   - AI-powered article writing
   - Customizable word count (default: 3200)
   - SEO optimization
   - Custom outline support

2. Media Integration:

   - Automatic image selection from Unsplash
   - Image optimization and resizing
   - YouTube video embedding
   - Featured image selection

3. WordPress Integration:

   - Direct posting to WordPress
   - Category and tag management
   - Media library integration
   - Post scheduling

4. Data Management:
   - CSV/Excel input support
   - Content caching
   - Version control
   - Detailed logging

## Installation

### Standalone Version

1. Clone the repository:

```bash
git clone https://github.com/yourusername/wordpress_automation.git
cd wordpress_automation
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install requirements:

```bash
pip install -r requirements.txt
```

4. Set up configuration:

```bash
cp config/config.example.ini config/config.ini
# Edit config.ini with your credentials
```

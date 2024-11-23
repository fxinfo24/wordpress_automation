# setup.py
from setuptools import setup, find_packages

setup(
    name="wordpress_automation",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'python-wordpress-xmlrpc>=2.3.0',
        'requests>=2.31.0',
        'Pillow>=10.1.0',
        'google-api-python-client>=2.108.0',
        'pandas>=2.1.3',
        'openai>=1.3.5',
        'python-dotenv>=1.0.0',
        'pytest>=7.4.3',
        'ratelimit>=2.2.1',
        'configparser>=6.0.0',
    ],
    author="The Saint",
    author_email="fxinfo24@gmail.com",
    description="WordPress content automation tool",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
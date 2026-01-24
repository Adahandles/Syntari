#!/usr/bin/env python3
"""
Setup script for Syntari Programming Language
"""

from setuptools import setup, find_packages
import os

# Read the requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read the README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='syntari',
    version='0.3.0',
    description='AI-integrated, type-safe, functional-first programming language',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='DeuOS, LLC',
    author_email='legal@deuos.io',
    url='https://github.com/Adahandles/Syntari',
    packages=find_packages(exclude=['tests*', 'examples*']),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'syntari=src.interpreter.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='programming-language compiler interpreter ai',
    project_urls={
        'Source': 'https://github.com/Adahandles/Syntari',
    },
)

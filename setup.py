"""
Setup configuration for RPG Game.

Allows the project to be installed as a package with:
  pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="rpg-game",
    version="0.1.0",
    description="A modular CLI RPG game engine with combat, quests, and NPCs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/afran1993/rpg-game",
    license="MIT",
    
    # Package discovery
    packages=find_packages(exclude=["tests", "tools"]),
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Runtime dependencies (currently none, using only stdlib)
    install_requires=[],
    
    # Optional dependencies for development
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "pylint>=2.0",
            "black>=22.0",
            "mypy>=0.900",
        ],
    },
    
    # Console scripts
    entry_points={
        "console_scripts": [
            "rpg-game=main:main",
        ],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Role-Playing",
    ],
    
    # Keywords for finding the project
    keywords="rpg game cli text-adventure",
)

"""
Configuration and path constants.
"""

from pathlib import Path
from importlib.resources import files

# Data directory in user's home folder (separate from code)
DATA_DIR = Path.home() / "reading-companion-data"
BOOKSTACKS_DIR = DATA_DIR / "bookstacks"
PROGRESS_DIR = DATA_DIR / "progress"
REFLECTIONS_DIR = DATA_DIR / "reflections"
AUTHORS_DIR = DATA_DIR / "authors"

# Prompts are bundled inside the package for distribution
PROMPTS_DIR = files("reading_companion.prompts")


def ensure_dirs():
    """Create all necessary directories if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    BOOKSTACKS_DIR.mkdir(exist_ok=True)
    PROGRESS_DIR.mkdir(exist_ok=True)
    REFLECTIONS_DIR.mkdir(exist_ok=True)
    AUTHORS_DIR.mkdir(exist_ok=True)

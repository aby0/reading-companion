"""
JSON storage utilities.
"""

import json
import re
from pathlib import Path

from .config import DATA_DIR, PROMPTS_DIR, ensure_dirs


def load_json(name: str, subdir: Path = None) -> dict:
    """
    Load a JSON file from the data directory.

    Args:
        name: File name without .json extension
        subdir: Optional subdirectory (e.g., PROGRESS_DIR)

    Returns:
        Parsed JSON as dict, or empty dict if file doesn't exist
    """
    directory = subdir or DATA_DIR
    path = directory / f"{name}.json"
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_json(name: str, data: dict, subdir: Path = None) -> None:
    """
    Save data to a JSON file.

    Args:
        name: File name without .json extension
        data: Dictionary to save
        subdir: Optional subdirectory
    """
    ensure_dirs()
    directory = subdir or DATA_DIR
    path = directory / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_prompt(name: str) -> str:
    """Load a prompt template from the package."""
    prompt_file = PROMPTS_DIR.joinpath(f"{name}.md")
    try:
        return prompt_file.read_text()
    except FileNotFoundError:
        return f"Prompt '{name}' not found"


def slugify(text: str) -> str:
    """
    Convert text to a filename-safe slug.
    Example: "Anna Karenina" -> "anna-karenina"
    """
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text

# utils.py
# Shared utility functions

import re


def is_valid_youtube_url(url: str) -> bool:
    """Quick regex check before we try to parse the URL."""
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    return bool(re.match(pattern, url.strip()))


def truncate_text(text: str, max_chars: int = 300) -> str:
    """Return a truncated preview of a long string."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."

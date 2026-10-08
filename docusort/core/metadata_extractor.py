from __future__ import annotations

from datetime import date
from pathlib import Path


class MetadataExtractor:
    """Simple metadata extractor placeholder for the first app version."""

    @staticmethod
    def extract(path: Path) -> dict[str, str]:
        stem = path.stem.replace("_", " ").replace("-", " ")
        today = date.today().isoformat()

        return {
            "title": stem.title() if stem else "Document",
            "company": "Unknown",
            "date": today,
            "category": "General",
        }

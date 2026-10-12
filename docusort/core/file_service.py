from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass
class DocumentCandidate:
    source_path: Path
    name: str
    topic: str
    date: str


class FileService:
    @staticmethod
    def list_files(directory: Path, recursive: bool = True) -> list[Path]:
        if not directory.is_dir():
            return []
        candidates = directory.rglob("*") if recursive else directory.iterdir()
        return sorted(
            [path for path in candidates if path.is_file() and not path.name.startswith(".")],
            key=lambda item: item.relative_to(directory).as_posix().lower(),
        )

    @staticmethod
    def sanitize_name(value: str) -> str:
        clean = "".join(ch if ch.isalnum() or ch in {"_", "-", " ".strip()} else "_" for ch in value.strip())
        clean = "_".join(part for part in clean.split() if part)
        return clean or "document"

    @staticmethod
    def build_date_value(date_value: str, date_format: str) -> str:
        if not date_value:
            return ""

        try:
            parsed = datetime.fromisoformat(date_value)
        except ValueError:
            return date_value

        if date_format == "YYYY-MM-dd":
            return parsed.strftime("%Y-%m-%d")
        if date_format == "YYYY-MM":
            return parsed.strftime("%Y-%m")
        if date_format == "YYYY":
            return parsed.strftime("%Y")
        return ""

    @staticmethod
    def generate_target_name(date_value: str, topic: str, name: str, extension: str, date_format: str) -> str:
        date_prefix = FileService.build_date_value(date_value, date_format)
        topic_name = FileService.sanitize_name(topic)
        document_name = FileService.sanitize_name(name)

        if date_prefix:
            base = f"{date_prefix}_{topic_name}_{document_name}"
        else:
            base = f"{topic_name}_{document_name}"

        return f"{base}{extension}"

    @staticmethod
    def ensure_unique_destination(directory: Path, filename: str) -> Path:
        destination = directory / filename
        if not destination.exists():
            return destination

        stem = destination.stem
        suffix = 2
        while True:
            candidate = directory / f"{stem}_{suffix}{destination.suffix}"
            if not candidate.exists():
                return candidate
            suffix += 1

    @staticmethod
    def move_to_destination(source_path: Path, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        target = destination if destination.exists() is False else FileService.ensure_unique_destination(destination.parent, destination.name)
        source_path.replace(target)
        return target

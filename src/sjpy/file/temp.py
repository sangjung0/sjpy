from __future__ import annotations

import tempfile
import uuid

from pathlib import Path


def create_temp_path(suffix: str = "") -> Path:
    temp_dir = Path(tempfile.gettempdir())
    while True:
        p = temp_dir / f"temp_{uuid.uuid4().hex}{suffix}"
        if not p.exists():
            return p


__all__ = ["create_temp_path"]

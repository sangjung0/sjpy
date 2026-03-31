from __future__ import annotations

import logging

from pathlib import Path
from rich.logging import RichHandler


def generate(
    name: str,
    level: int = logging.INFO,
    path: str | Path | None = None,
    file_log_level: int = logging.DEBUG,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(min(level, file_log_level))
    logger.propagate = False

    console_formatter = logging.Formatter("%(message)s")
    file_formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    rich_handler = None
    for handler in logger.handlers:
        if isinstance(handler, RichHandler):
            rich_handler = handler
            break

    if rich_handler is None:
        rich_handler = RichHandler(
            show_level=True, show_time=True, rich_tracebacks=True, show_path=True
        )
        rich_handler.setLevel(level)
        rich_handler.setFormatter(console_formatter)
        logger.addHandler(rich_handler)
    else:
        rich_handler.setLevel(level)
        rich_handler.setFormatter(console_formatter)

    if path is not None:
        path = Path(path)
        file_path = path / f"{name}.log"

        for handler in logger.handlers:
            if (
                isinstance(handler, logging.FileHandler)
                and Path(handler.baseFilename) == file_path
            ):
                handler.setLevel(file_log_level)
                break
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setLevel(file_log_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    return logger


__all__ = ["generate"]

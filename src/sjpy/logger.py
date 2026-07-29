from __future__ import annotations

import logging

from pathlib import Path
from rich.logging import RichHandler


def configure_logger(
    name: str,
    level: int = logging.INFO,
    path: str | Path | None = None,
    file_log_level: int = logging.DEBUG,
) -> logging.Logger:
    logger = logging.getLogger(name)
    for handler in logger.handlers.copy():
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(min(level, file_log_level))
    logger.propagate = False

    console_handler = RichHandler(
        show_level=True,
        show_time=True,
        rich_tracebacks=True,
        show_path=True,
    )
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)

    if path is not None:
        path = Path(path)
        if path.is_file():
            file_path = path
        else:
            file_path = Path(path) / f"{name}.log"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)

    return logger


__all__ = ["configure_logger"]

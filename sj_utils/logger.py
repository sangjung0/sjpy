import logging

from pathlib import Path
from rich.logging import RichHandler


def generate(
    name: str,
    level: int = logging.INFO,
    path: Path = None,
    file_log_level: int = logging.DEBUG,
):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not any(isinstance(h, RichHandler) for h in logger.handlers):
        logger.addHandler(RichHandler())

    if path is not None:
        file_path = path / f"{name}.log"
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(
                file_path
            ):
                handler.setLevel(file_log_level)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setLevel(file_log_level)
            logger.addHandler(file_handler)

    return logger

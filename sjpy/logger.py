import logging

from pathlib import Path
from rich.logging import RichHandler


def generate(
    name: str,
    level: int = logging.INFO,
    path: str | Path | None = None,
    file_log_level: int = logging.DEBUG,
):
    logger = logging.getLogger(name)
    logger.setLevel(min(level, file_log_level))
    logger.propagate = False

    if not any(isinstance(h, RichHandler) for h in logger.handlers):
        console_handler = RichHandler()
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    if path is not None:
        path = Path(path)
        file_path = path / f"{name}.log"
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler) and handler.baseFilename == str(
                file_path
            ):
                handler.setLevel(file_log_level)
                break
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setLevel(file_log_level)
            logger.addHandler(file_handler)

    return logger


__all__ = ["generate"]

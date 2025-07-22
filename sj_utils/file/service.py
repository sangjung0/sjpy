import os
import re

from dotenv import load_dotenv

PATTERN = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")

load_dotenv()


def replace(d: dict):
    for k, v in d.items():
        if isinstance(v, dict):
            replace(v)
        elif isinstance(v, list):
            for idx in range(len(v)):
                if isinstance(v[idx], dict):
                    replace(v[idx])
                elif isinstance(v[idx], str):
                    v[idx] = PATTERN.sub(replacer, v[idx])
        elif isinstance(v, str):
            d[k] = PATTERN.sub(replacer, v)


def replacer(match: re.Match[str]) -> str:
    return os.getenv(match.group(1), match.group(2))


__all__ = ["replace", "replacer"]

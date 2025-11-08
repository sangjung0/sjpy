import os
import re

from dotenv import load_dotenv

PATTERN = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")

load_dotenv()


def replace(d: dict, replace_data: dict = None):
    replace_data = replace_data or {}
    replace_data.update(os.environ)

    for k, v in d.items():
        if isinstance(v, dict):
            replace(v, replace_data)
        elif isinstance(v, list):
            for idx in range(len(v)):
                if isinstance(v[idx], dict):
                    replace(v[idx], replace_data)
                elif isinstance(v[idx], str):
                    v[idx] = PATTERN.sub(lambda m: replacer(m, replace_data), v[idx])
        elif isinstance(v, str):
            d[k] = PATTERN.sub(lambda m: replacer(m, replace_data), v)


def replacer(match: re.Match[str], replace_data: dict) -> str:
    return replace_data.get(match.group(1), match.group(2))


__all__ = ["replace", "replacer"]

import re
import unicodedata


def camel_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def normalize_text_only_en(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def remove_spaces_and_symbols(text: str) -> str:
    return "".join(
        ch
        for ch in text
        if not unicodedata.category(ch).startswith(("P", "S")) and not ch.isspace()
    )


__all__ = [
    "camel_to_snake",
    "normalize_text_only_en",
    "remove_spaces_and_symbols",
]

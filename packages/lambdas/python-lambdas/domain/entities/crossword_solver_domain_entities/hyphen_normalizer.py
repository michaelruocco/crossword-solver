import re

_HYPHEN_PATTERN = re.compile(r"[–—‐\-−⁃‒]")
_TRIPLE_HYPHEN_PATTERN = re.compile(r"\s*-\s*-\s*-\s*")
_SPACE_BEFORE_COMMA_PATTERN = re.compile(r"\s+,")


def normalize_hyphens(value: str) -> str:
    normalized = _HYPHEN_PATTERN.sub("-", value)
    normalized = _TRIPLE_HYPHEN_PATTERN.sub(" - - - ", normalized)

    # A comma immediately following the triple hyphen should not have
    # a preceding space.
    normalized = _SPACE_BEFORE_COMMA_PATTERN.sub(",", normalized)

    return normalized.strip()

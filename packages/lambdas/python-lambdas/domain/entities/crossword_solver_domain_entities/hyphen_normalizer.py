import re

_HYPHEN_PATTERN = re.compile(r"[–—‐\-−⁃‒]")
_TRIPLE_HYPHEN_PATTERN = re.compile(r"-\s*-\s*-")


def normalize_hyphens(value: str) -> str:
    normalized = _HYPHEN_PATTERN.sub("-", value)
    normalized = _normalize_triple_hyphens(normalized)

    # A comma immediately following the triple hyphen should not have
    # a preceding space.
    normalized = _remove_space_before_commas(normalized)

    return normalized.strip()


def _normalize_triple_hyphens(value: str) -> str:
    parts = _TRIPLE_HYPHEN_PATTERN.split(value)
    last = len(parts) - 1
    trimmed = [part.lstrip() if i > 0 else part for i, part in enumerate(parts)]
    trimmed = [part.rstrip() if i < last else part for i, part in enumerate(trimmed)]
    return " - - - ".join(trimmed)


def _remove_space_before_commas(value: str) -> str:
    parts = value.split(",")
    return ",".join([part.rstrip() for part in parts[:-1]] + parts[-1:])

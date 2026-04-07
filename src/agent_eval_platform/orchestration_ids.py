import hashlib

_PART_SEPARATOR = "\x1f"


def build_orchestration_id(prefix: str, *parts: str) -> str:
    payload = _PART_SEPARATOR.join(parts)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"

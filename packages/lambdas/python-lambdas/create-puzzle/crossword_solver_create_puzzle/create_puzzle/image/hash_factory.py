import hashlib


class HashFactory:
    def to_hash(self, value: str | bytes) -> str:
        if isinstance(value, str):
            value = value.encode("utf-8")

        return hashlib.sha256(value).hexdigest()

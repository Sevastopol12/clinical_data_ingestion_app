import base64
from hashlib import sha3_256


def encode_content(raw_bytes: bytes) -> str:
    encoded_bytes = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
    return encoded_bytes


def hash_content(encoded_bytes: str) -> str:
    sha_object = sha3_256()
    sha_object.update(encoded_bytes.encode())

    return sha_object.hexdigest()


__all__ = ["encode_content", "hash_content"]

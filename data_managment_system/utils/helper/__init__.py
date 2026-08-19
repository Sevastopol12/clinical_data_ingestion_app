import base64


def encode_content(raw_bytes: bytes) -> str:
    encoded_bytes = base64.b64encode(raw_bytes).decode("utf-8")
    return encoded_bytes


__all__ = ["encode_content"]

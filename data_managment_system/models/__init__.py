from pydantic import BaseModel


class File(BaseModel):
    filename: str
    encoded_content: str


class FileBatch(BaseModel):
    files: list[File]


__all__ = ["FileBatch", "File"]

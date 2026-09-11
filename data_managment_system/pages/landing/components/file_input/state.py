import reflex as rx
from io import BytesIO
from typing import Optional


class FileInputState(rx.State):
    uploaded_files: dict[str, bytes]

    @rx.var
    def get_uploaded_files(self) -> list[str]:
        return [file for file in self.uploaded_files.keys()]

    @rx.event(background=True)
    async def dump_files(self, chunk_iter: rx.UploadChunkIterator):
        async for chunk in chunk_iter:
            filename = chunk.filename
            data = chunk.data

            async with self:
                if self.uploaded_files.get(filename) is None:
                    self.uploaded_files[filename] = b""

                self.uploaded_files[filename] += data

    @rx.event
    def remove_file(self, filename: str):
        try:
            self.uploaded_files.pop(filename)

            return rx.toast.success(f"Item remove: {filename}")

        except Exception as e:
            return rx.toast.error(f"Error {e}")

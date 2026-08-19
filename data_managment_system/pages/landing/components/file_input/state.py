import reflex as rx
import requests
import os

from pydantic import ValidationError
from dotenv import load_dotenv

from data_managment_system.models import File, FileBatch
from data_managment_system.utils.helper import encode_content


load_dotenv()


class FileInputState(rx.State):
    uploaded_files: dict[str, bytes]

    @rx.var
    def get_uploaded_files(self) -> list[str]:
        return [file for file in self.uploaded_files.keys()]

    @rx.event(background=True)
    async def upload_files(self, chunk_iter: rx.UploadChunkIterator):
        async for chunk in chunk_iter:
            filename = chunk.filename
            data = chunk.data

            async with self:
                if self.uploaded_files.get(filename) is None:
                    self.uploaded_files[filename] = b""

                self.uploaded_files[filename] += data

    @rx.event(background=True)
    async def dump_files(self):
        try:
            # Check emptiness
            if len(self.uploaded_files) < 1:
                raise Exception("There's no file uploaded, donut.")

            # Implement payload
            file_batch: list[File] = []

            for filename, content in self.uploaded_files.items():
                file_batch.append(
                    File(
                        filename=filename,
                        encoded_content=encode_content(raw_bytes=content),
                    )
                )

            # Push
            requests.post(
                url=os.getenv("BACKEND_URL"),
                data={"file_batch": FileBatch(files=file_batch)},
            )

            # Clean up
            async with self:
                self.clear_all_files()

            return rx.toast.success("Success, files dumped.")

        except ValidationError:
            return rx.toast.error("Internal. Mismatch field content")

        except Exception as e:
            return rx.toast.error(f"Error: {e}")

    @rx.event
    def remove_file(self, filename: str):
        try:
            self.uploaded_files.pop(filename)

            return rx.toast.success(f"Item remove: {filename}")

        except Exception as e:
            return rx.toast.error(f"Error {e}")

    @rx.event
    def clear_all_files(self):
        self.uploaded_files = {}

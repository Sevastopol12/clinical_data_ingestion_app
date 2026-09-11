import reflex as rx
import logging
from asyncio import create_task, gather

from .utils import extract_csv_excel_headers, _load_to_storage, _record_file
from data_managment_system.models import (
    IngestionCreate,
    IngestionComplete,
    IngestionDetail,
    FileStatus,
)
from data_managment_system.utils.helper import encode_content, hash_content

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class FileInputState(rx.State):
    uploaded_files: dict[str, bytes] = {}
    uploaded_files_ref: set = set()
    file_columns: dict[str, list[str]] = {}
    column_mappings: dict[str, dict[str, str]] = {}
    selected_file: str = ""
    is_uploading: bool = False

    @rx.var
    def get_uploaded_files(self) -> list[str]:
        return list(self.uploaded_files.keys())

    @rx.event(background=True)
    async def upload_files(self, chunk_iter: rx.UploadChunkIterator):
        before_length = len(self.uploaded_files_ref)
        async for chunk in chunk_iter:
            filename = chunk.filename
            data = chunk.data

            if filename in self.uploaded_files_ref:
                continue

            async with self:
                if filename not in self.uploaded_files:
                    self.uploaded_files[filename] = b""
                self.uploaded_files[filename] += data

        after_length = len(self.uploaded_files_ref)

        for filename in list(self.uploaded_files.keys())[before_length:after_length]:
            self.uploaded_files_ref.add(filename)

        # Parse headers for both CSV and XLSX files
        async with self:
            for filename, content in self.uploaded_files.items():
                if filename not in self.file_columns:
                    headers = extract_csv_excel_headers(filename, content)
                    self.file_columns[filename] = headers
                    self.column_mappings[filename] = {col: col for col in headers}

    @rx.event
    def select_file(self, filename: str):
        if self.selected_file == filename:
            self.selected_file = ""
        else:
            self.selected_file = filename

    @rx.event
    def update_mapping(self, filename: str, source_col: str, target_col: str):
        if filename in self.column_mappings:
            self.column_mappings[filename][source_col] = target_col

    @rx.event
    def remove_file(self, filename: str):
        # Remove file reference
        self.uploaded_files.pop(filename, None)
        self.uploaded_files_ref.discard(filename)

        # Remove file data
        self.file_columns.pop(filename, None)
        self.column_mappings.pop(filename, None)

        if self.selected_file == filename:
            self.selected_file = ""
        return rx.toast.success(f"Removed: {filename}")

    @rx.event
    def clear_all_files(self):
        self.uploaded_files.clear()
        self.uploaded_files_ref.clear()

        self.file_columns.clear()
        self.column_mappings.clear()

        self.selected_file = ""
        return rx.toast.info("All files removed.")

    @rx.event(background=True)
    async def dump_files(self):
        try:
            async with self:
                if len(self.uploaded_files) < 1:
                    yield rx.toast.warning("No files uploaded.")
                    return
                self.is_uploading = True

            # Register
            files = self._register_batch()

            # Load to storage
            upload_responses = await create_task(_load_to_storage(list(files.values())))

            failed_files: list[str] = []
            grouped_requests: list[IngestionDetail] = []

            for response in upload_responses:
                if response.status != FileStatus.CREATED:
                    failed_files.append(response.filename)
                    logger.error(
                        f"Failed {response.filename}: {response.error_message}"
                    )
                grouped_requests.append(
                    IngestionDetail(
                        response=response, metadata=files.get(response.filename)
                    )
                )

            # Record
            record_files = self._create_record(grouped_requests)
            record_task = create_task(_record_file(record_files))

            # Update UI
            async with self:
                for file in grouped_requests:
                    if file.response.status == FileStatus.CREATED:
                        self.remove_file(file.metadata.filename)
                        if self.selected_file == file.metadata.filename:
                            self.selected_file = ""

                self.is_uploading = False

            if failed_files:
                yield rx.toast.error(f"Failed: {', '.join(failed_files)}")
            else:
                yield rx.toast.success("Success, all files dumped and recorded.")

            await gather(record_task)

        except Exception as exc:
            rx.toast.error(exc)
            async with self:
                self.is_uploading = False
            raise

    def _register_batch(self) -> dict[str, IngestionCreate]:
        return {
            filename: IngestionCreate(filename=filename, content=content)
            for filename, content in self.uploaded_files.items()
        }

    def _create_record(
        self, succeed_files: set[IngestionDetail]
    ) -> list[IngestionComplete]:
        return [
            IngestionComplete(
                id=detail.response.id,
                content_hash=hash_content(encode_content(detail.metadata.content)),
                size_bytes=int(len(detail.metadata.content)),
                mappings=self.column_mappings.get(detail.metadata.filename, None),
            )
            for detail in succeed_files
        ]

import logging

import reflex as rx

from data_managment_system.config import settings
from data_managment_system.models import (
    FileStatus,
    IngestionComplete,
    IngestionCreate,
    IngestionDetail,
    MappingRequest,
)
from data_managment_system.services.ingestion import (
    _fetch_all_column_mappings,
    _load_to_storage,
    _record_file,
    encode_content,
    hash_content,
)
from data_managment_system.utils.headers import extract_csv_excel_headers

logger = logging.getLogger(__name__)


class FileInputState(rx.State):
    uploaded_files: dict[str, bytes] = {}  # noqa: RUF012
    column_mappings: dict[str, dict[str, str]] = {}  # noqa: RUF012
    selected_file: str = ""
    is_uploading: bool = False

    @rx.var
    def get_uploaded_files(self) -> list[str]:
        return list(self.uploaded_files.keys())

    @rx.var
    def get_column_mappings(self) -> list[str]:
        return list(self.column_mappings.get(self.selected_file, {}).keys())

    @rx.event
    def reject_file_upload(self):
        return rx.toast.error("Invalid format.")

    @rx.event(background=True)
    async def upload_files(self, chunk_iter: rx.UploadChunkIterator):
        tracked_files = set(self.uploaded_files)
        buffers: dict[str, bytearray] = {}

        async for chunk in chunk_iter:
            filename = chunk.filename
            if filename in tracked_files:
                continue
            buffers.setdefault(filename, bytearray()).extend(chunk.data)

        new_files = {filename: bytes(buffer) for filename, buffer in buffers.items()}

        async with self:
            self.uploaded_files.update(new_files)

        map_requests = [
            MappingRequest(
                filename=filename,
                columns=extract_csv_excel_headers(filename, content),
            )
            for filename, content in new_files.items()
        ]
        map_results = await _fetch_all_column_mappings(map_requests)

        async with self:
            for request in map_requests:
                self.column_mappings[request.filename] = {
                    column: column for column in request.columns
                }
            for result in map_results:
                self.column_mappings[result.filename] = {
                    column: target or ""
                    for column, target in (result.mapping or {}).items()
                }

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
        self.column_mappings.pop(filename, None)

        if self.selected_file == filename:
            self.selected_file = ""
        return rx.toast.success(f"Removed: {filename}")

    @rx.event
    def clear_all_files(self):
        self.uploaded_files.clear()
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
            files = self._create_upload_requests()

            # Load to storage
            upload_responses = await _load_to_storage(list(files.values()))

            # Handle upload results
            failed_files: list[str] = []
            grouped_requests: list[IngestionDetail] = []
            for file, response in zip(files.values(), upload_responses):
                if isinstance(response, Exception):
                    failed_files.append(file.filename)
                    logger.error("Failed %s: %s", file.filename, response)
                    continue

                if response.status != FileStatus.CREATED:
                    failed_files.append(response.filename or file.filename)
                    logger.error("Failed %s: %s", file.filename, response.error_message)

                grouped_requests.append(
                    IngestionDetail(response=response, metadata=file)
                )

            # Update UI
            async with self:
                for file in grouped_requests:
                    if file.response.status == FileStatus.CREATED:
                        self.remove_file(  # TODO(B4): yield chained event
                            file.metadata.filename
                        )
                        if self.selected_file == file.metadata.filename:
                            self.selected_file = ""

                self.is_uploading = False

            if failed_files:
                yield rx.toast.error(f"Failed: {', '.join(failed_files)}")
            else:
                yield rx.toast.success("Success, all files dumped and recorded.")

            # Record
            record_files = self._create_record_requests(grouped_requests)
            await _record_file(record_files)

        except Exception as exc:
            rx.toast.error(str(exc))  # TODO(B4): yield this toast event
            async with self:
                self.is_uploading = False
            raise

    def _create_upload_requests(self) -> dict[str, IngestionCreate]:
        return {
            filename: IngestionCreate(
                filename=filename,
                content=content,
                facility_id=settings.dev_facility_id,  # TODO(B2: from AuthState)
            )
            for filename, content in self.uploaded_files.items()
        }

    def _create_record_requests(
        self, succeed_files: list[IngestionDetail]
    ) -> list[IngestionComplete]:
        return [
            IngestionComplete(
                id=detail.response.id,
                content_hash=hash_content(
                    encode_content(detail.metadata.content or b"")
                ),
                size_bytes=len(detail.metadata.content or b""),
                mappings=self.column_mappings.get(detail.metadata.filename, None),
            )
            for detail in succeed_files
        ]

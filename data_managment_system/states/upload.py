"""State for the upload dialog and its file mapping workflow."""

import asyncio
import logging
from uuid import UUID

import reflex as rx

from data_managment_system.copy import UPLOAD
from data_managment_system.models import MappingRequest
from data_managment_system.models.ingestion import MAX_BATCH_FILES, MAX_FILE_BYTES
from data_managment_system.services.http import default_context
from data_managment_system.services.ingestion import (
    UploadJob,
    fetch_mapping_suggestions,
    submit_batch,
)
from data_managment_system.utils.headers import HeaderError, extract_csv_excel_headers
from data_managment_system.utils.upload_rules import (
    FileVM,
    IncomingFile,
    MappingRowVM,
    admit_files,
    apply_suggestions,
    format_file_size,
    normalize_target,
    to_record_mappings,
    unique_sources,
    validate_rows,
)

logger = logging.getLogger(__name__)


class FileInputState(rx.State):
    _files: dict[str, bytes] = {}  # noqa: RUF012
    _ingestion_ids: dict[str, UUID] = {}  # noqa: RUF012
    _revisions: dict[str, int] = {}  # noqa: RUF012
    _revision_counter: int = 0

    files: list[FileVM] = []  # noqa: RUF012
    expanded_files: list[str] = []  # noqa: RUF012
    dialog_open: bool = False
    is_submitting: bool = False

    @rx.var
    def file_count(self) -> int:
        return len(self.files)

    @rx.var
    def count_label(self) -> str:
        return UPLOAD["files_ready"].format(count=len(self.files), max=MAX_BATCH_FILES)

    @rx.var
    def has_files(self) -> bool:
        return bool(self.files)

    @rx.var
    def can_submit(self) -> bool:
        return (
            bool(self.files)
            and not self.is_submitting
            and not any(file.mapping_pending for file in self.files)
        )

    @rx.event
    def open_dialog(self) -> None:
        self.dialog_open = True

    @rx.event
    def set_dialog_open(self, value: bool) -> None:
        self.dialog_open = value

    @rx.event
    def toggle_mapping(self, filename: str) -> None:
        if not any(file.filename == filename for file in self.files):
            return
        if filename in self.expanded_files:
            self.expanded_files = [
                item for item in self.expanded_files if item != filename
            ]
        else:
            self.expanded_files = [*self.expanded_files, filename]

    @staticmethod
    def _kind(filename: str) -> str:
        return filename.rsplit(".", 1)[-1].upper()

    @staticmethod
    def _rejection_label(rejected: dict[str, int]) -> str:
        labels = {
            "bad_type": "unsupported file type",
            "oversize": "files over 5 MB",
            "batch_full": "files beyond the 10-file limit",
        }
        return ", ".join(
            f"{count} {labels.get(reason, reason)}"
            for reason, count in rejected.items()
        )

    @staticmethod
    def _header_details(errors: dict[str, HeaderError]) -> str:
        items = [
            f"{filename}: {UPLOAD[f'header_reason_{error.reason.value}']}"
            for filename, error in errors.items()
        ]
        if len(items) <= 3:
            return "; ".join(items)
        return "; ".join(items[:3]) + f"; and {len(items) - 3} more"

    @staticmethod
    async def _read_headers(filename: str, content: bytes) -> list[str]:
        return await asyncio.to_thread(extract_csv_excel_headers, filename, content)

    @rx.event
    def reject_files(self, *_args: object) -> object:
        return rx.toast.error(
            UPLOAD["toast_rejected"].format(details="unsupported files")
        )

    @rx.event(background=True)
    async def upload_files(self, chunk_iter: rx.UploadChunkIterator):
        max_bytes = MAX_FILE_BYTES
        buffers: dict[str, bytearray] = {}
        sizes: dict[str, int] = {}
        oversize: set[str] = set()
        async for chunk in chunk_iter:
            filename = chunk.filename
            size = sizes.get(filename, 0) + len(chunk.data)
            sizes[filename] = size
            if size > max_bytes:
                oversize.add(filename)
            remaining = max(0, max_bytes - len(buffers.get(filename, b"")))
            if remaining:
                buffers.setdefault(filename, bytearray()).extend(chunk.data[:remaining])

        if self.is_submitting:
            yield rx.toast.warning(UPLOAD["toast_busy"])
            return

        incoming = [
            IncomingFile(filename, sizes[filename], filename in oversize)
            for filename in buffers
        ]
        admission = admit_files([file.filename for file in self.files], incoming)
        if admission.rejected:
            yield rx.toast.warning(
                UPLOAD["toast_rejected"].format(
                    details=self._rejection_label(admission.rejected)
                )
            )

        header_errors: dict[str, HeaderError] = {}
        prepared: list[tuple[str, bytes, list[str]]] = []
        for item in admission.admitted:
            try:
                content = bytes(buffers[item.filename])
                headers = await self._read_headers(item.filename, content)
            except HeaderError as exc:
                header_errors[item.filename] = exc
                continue
            prepared.append((item.filename, content, headers))

        if header_errors:
            yield rx.toast.error(
                UPLOAD["toast_header_failed"].format(
                    details=self._header_details(header_errors)
                )
            )
        if not prepared:
            return

        async with self:
            new_files: list[FileVM] = []
            for filename, content, headers in prepared:
                self.expanded_files = [
                    item for item in self.expanded_files if item != filename
                ]
                self._revision_counter += 1
                self._revisions[filename] = self._revision_counter
                self._files[filename] = content
                rows = [
                    MappingRowVM(source=source) for source in unique_sources(headers)
                ]
                new_files.append(
                    FileVM(
                        filename=filename,
                        size_bytes=len(content),
                        size_label=format_file_size(len(content)),
                        kind=self._kind(filename),
                        mapping_pending=True,
                        rows=rows,
                    )
                )
            positions = {file.filename: index for index, file in enumerate(self.files)}
            updated = list(self.files)
            for file in new_files:
                if file.filename in positions:
                    updated[positions[file.filename]] = file
                else:
                    positions[file.filename] = len(updated)
                    updated.append(file)
            self.files = updated
            revisions = {
                file.filename: self._revisions[file.filename] for file in new_files
            }

        requests = [
            MappingRequest(
                filename=file.filename, columns=[row.source for row in file.rows]
            )
            for file in new_files
        ]
        suggestions = await fetch_mapping_suggestions(requests)
        async with self:
            updated = list(self.files)
            for request, suggestion in zip(requests, suggestions):
                index = next(
                    (
                        i
                        for i, file in enumerate(updated)
                        if file.filename == request.filename
                    ),
                    None,
                )
                if (
                    index is None
                    or self._revisions.get(request.filename)
                    != revisions[request.filename]
                ):
                    continue
                file = updated[index]
                rows = (
                    apply_suggestions(file.rows, suggestion.mapping)
                    if suggestion is not None and suggestion.mapping is not None
                    else file.rows
                )
                updated[index] = file.model_copy(
                    update={"rows": rows, "mapping_pending": False}
                )
            self.files = updated

    @rx.event
    def set_target(self, filename: str, source: str, value: str) -> None:
        self._update_rows(filename, source, value, "")

    @rx.event
    def blur_target(self, filename: str, source: str) -> None:
        file = next((item for item in self.files if item.filename == filename), None)
        if file is None:
            return
        row = next((item for item in file.rows if item.source == source), None)
        if row is None:
            return
        try:
            value = normalize_target(row.target)
            error = ""
        except ValueError:
            value = row.target
            error = "empty-normalized"
        self._update_rows(filename, source, value or "", error)
        self._validate_file(filename)

    def _update_rows(
        self, filename: str, source: str, target: str, error: str | None
    ) -> None:
        for index, file in enumerate(self.files):
            if file.filename != filename:
                continue
            rows = [
                row.model_copy(
                    update={
                        "target": target,
                        **({"error": error} if error is not None else {}),
                    }
                )
                if row.source == source
                else row
                for row in file.rows
            ]
            self.files[index] = file.model_copy(update={"rows": rows})
            return

    def _validate_file(self, filename: str) -> None:
        for index, file in enumerate(self.files):
            if file.filename == filename:
                self.files[index] = file.model_copy(
                    update={"rows": validate_rows(file.rows)}
                )
                return

    @rx.event
    def remove_file(self, filename: str) -> None:
        if not self.is_submitting:
            self._drop_file(filename)

    @rx.event
    def clear_all(self) -> None:
        if self.is_submitting:
            return
        self.files = []
        self._files.clear()
        self._ingestion_ids.clear()
        self._revisions.clear()
        self.expanded_files = []

    def _drop_file(self, filename: str) -> None:
        self._files.pop(filename, None)
        self._ingestion_ids.pop(filename, None)
        self._revisions.pop(filename, None)
        self.expanded_files = [item for item in self.expanded_files if item != filename]
        self.files = [file for file in self.files if file.filename != filename]

    async def _set_stage(self, filename: str, stage: str) -> None:
        async with self:
            for index, file in enumerate(self.files):
                if file.filename == filename:
                    self.files[index] = file.model_copy(update={"stage": stage})
                    return

    async def _stage_callback(self, filename: str, stage: str) -> None:
        await self._set_stage(filename, stage)

    @rx.event(background=True)
    async def submit_uploads(self):
        empty = False
        validation_error = False
        async with self:
            if self.is_submitting:
                return
            if not self.files:
                empty = True
                jobs: list[UploadJob] = []
            else:
                self.is_submitting = True
                validated: list[FileVM] = []
                for file in self.files:
                    rows = validate_rows(file.rows)
                    validation_error = validation_error or any(
                        row.error for row in rows
                    )
                    validated.append(file.model_copy(update={"rows": rows}))
                self.files = validated
                self.expanded_files = [
                    *self.expanded_files,
                    *[
                        file.filename
                        for file in validated
                        if any(row.error for row in file.rows)
                        and file.filename not in self.expanded_files
                    ],
                ]
                jobs = [
                    UploadJob(
                        filename=file.filename,
                        content=self._files[file.filename],
                        mappings=to_record_mappings(file.rows),
                        ingestion_id=self._ingestion_ids.get(file.filename),
                    )
                    for file in self.files
                ]

        if empty:
            yield rx.toast.warning(
                UPLOAD["toast_rejected"].format(details="no files selected")
            )
            return
        if validation_error:
            async with self:
                self.is_submitting = False
            yield rx.toast.error(UPLOAD["toast_fix_mapping"])
            return

        outcomes = await submit_batch(jobs, default_context(), self._stage_callback)
        successes = [outcome for outcome in outcomes if outcome.ok]
        failures = [outcome for outcome in outcomes if not outcome.ok]
        async with self:
            for outcome in outcomes:
                if outcome.ok:
                    self._drop_file(outcome.filename)
                    continue
                for index, file in enumerate(self.files):
                    if file.filename == outcome.filename:
                        self.files[index] = file.model_copy(
                            update={
                                "stage": "failed",
                                "failure_stage": outcome.failed_stage.value
                                if outcome.failed_stage
                                else "record",
                            }
                        )
                        if outcome.ingestion_id is not None:
                            self._ingestion_ids[outcome.filename] = outcome.ingestion_id
            self.is_submitting = False
            if failures:
                self.dialog_open = True
            else:
                self.dialog_open = False
        if failures:
            yield rx.toast.error(UPLOAD["toast_partial_failure"])
        else:
            yield rx.toast.success(UPLOAD["toast_success"])
        if successes:
            from data_managment_system.states.metrics import MetricsState

            yield MetricsState.refresh


__all__ = ["FileInputState"]

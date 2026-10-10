"""Backend state for the rejected-files dialog."""

from collections.abc import AsyncIterator
from typing import Any

import reflex as rx

from data_managment_system import copy
from data_managment_system.services import rejections as rejections_service
from data_managment_system.services.http import (
    Gone,
    NotFound,
    Unauthorized,
    Unavailable,
    get_client,
)
from data_managment_system.states.auth import AuthState
from data_managment_system.utils.builders import build_rejection_rows, mark_row_expired
from data_managment_system.utils.view_models import RejectionRowVM


class RejectionsState(rx.State):
    is_open: bool = False
    status: str = "idle"
    rows: list[RejectionRowVM] = []  # noqa: RUF012
    has_more: bool = False
    downloading_id: str = ""
    _cursor: str = ""
    _generation: int = 0

    @rx.event
    def open_dialog(self) -> Any:
        self.is_open = True
        if self.status in ("idle", "error"):
            return RejectionsState.refresh
        return None

    @rx.event
    def close_dialog(self) -> None:
        self.is_open = False

    @rx.event(background=True)
    async def refresh(self) -> AsyncIterator[Any]:
        async with self:
            self._generation += 1
            generation = self._generation
            self.status = "loading"
            self.rows = []
            self._cursor = ""
            self.has_more = False
            session = (await self.get_state(AuthState)).current_session()
        if session is None:
            async with self:
                self.status = "error"
            return
        try:
            page = await rejections_service.fetch_rejections(
                get_client(), access_token=session.token
            )
        except Unauthorized:
            yield AuthState.handle_unauthorized
            return
        except Unavailable:
            async with self:
                if generation == self._generation:
                    self.status = "503"
            return
        except Exception:  # noqa: BLE001
            async with self:
                if generation == self._generation:
                    self.status = "error"
            return
        async with self:
            if generation != self._generation:
                return
            self.rows = build_rejection_rows(page.items)
            self._cursor = page.next_cursor or ""
            self.has_more = bool(page.next_cursor)
            self.status = "ready" if self.rows else "empty"

    @rx.event(background=True)
    async def load_more(self) -> AsyncIterator[Any]:
        async with self:
            if not self.has_more or not self._cursor:
                return
            generation = self._generation
            cursor = self._cursor
            session = (await self.get_state(AuthState)).current_session()
        if session is None:
            return
        try:
            page = await rejections_service.fetch_rejections(
                get_client(), access_token=session.token, cursor=cursor
            )
        except Unauthorized:
            yield AuthState.handle_unauthorized
            return
        except Exception:  # noqa: BLE001
            yield rx.toast.warning(copy.REJECTIONS["toast_unavailable"])
            return
        async with self:
            if generation != self._generation:
                return
            self.rows = [*self.rows, *build_rejection_rows(page.items)]
            self._cursor = page.next_cursor or ""
            self.has_more = bool(page.next_cursor)
            self.status = "ready" if self.rows else "empty"

    @rx.event(background=True)
    async def download(self, file_id: str) -> AsyncIterator[Any]:
        async with self:
            if self.downloading_id:
                return
            self.downloading_id = file_id
            session = (await self.get_state(AuthState)).current_session()
        if session is None:
            async with self:
                self.downloading_id = ""
            return
        # NOTE: downloading_id is reset INSIDE each branch's own `async with self:`
        # block, before anything is yielded — not in a trailing `finally` after the
        # yield. A background event handler is backed by an asyncio.Task; if the
        # dialog is closed (or the page navigates) right as the file lands, the task
        # can be cancelled while paused inside a `finally` block's own `async with
        # self:` lock acquisition, which would skip that reset and leave the button
        # stuck in the spinning state. Resetting state before we ever yield an event
        # removes that race entirely.
        try:
            result = await rejections_service.fetch_download(
                get_client(), file_id, access_token=session.token
            )
        except Gone:
            async with self:
                self.rows = [
                    mark_row_expired(row) if row.file_id == file_id else row
                    for row in self.rows
                ]
                self.downloading_id = ""
            yield rx.toast(copy.REJECTIONS["toast_expired"])
            return
        except NotFound:
            async with self:
                self.rows = [row for row in self.rows if row.file_id != file_id]
                self.status = "ready" if self.rows else "empty"
                self.downloading_id = ""
            yield rx.toast(copy.REJECTIONS["toast_not_found"])
            return
        except Unavailable:
            async with self:
                self.downloading_id = ""
            yield rx.toast.warning(copy.REJECTIONS["toast_unavailable"])
            return
        except Unauthorized:
            async with self:
                self.downloading_id = ""
            yield AuthState.handle_unauthorized
            return
        except Exception:  # noqa: BLE001
            async with self:
                self.downloading_id = ""
            yield rx.toast.warning(copy.REJECTIONS["toast_failed"])
            return
        async with self:
            self.downloading_id = ""
        yield rx.download(url=rx.Var.create(result.download_url))

    @rx.event
    def clear_session(self) -> None:
        self.is_open = False
        self.status = "idle"
        self.rows = []
        self.has_more = False
        self.downloading_id = ""
        self._cursor = ""
        self._generation = 0

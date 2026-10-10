"""UI-only login state (show/hide password). Never holds the password."""

import reflex as rx


class LoginUiState(rx.State):
    """Toggle for the password visibility icon button."""

    show_password: bool = False

    @rx.event
    def toggle_password(self) -> None:
        """Flip password visibility."""
        self.show_password = not self.show_password

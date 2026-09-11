import reflex as rx
from .state import FileInputState


def upload_file_area() -> rx.Component:
    return rx.vstack(
        # Drag and Drop Upload Zone
        rx.upload(
            rx.vstack(
                rx.icon("upload", size=36, color=rx.color("accent", 9)),
                rx.text(
                    "Drag and drop CSV or XLSX files here, or click to browse",
                    font_weight="medium",
                    font_size="4",
                ),
                rx.text(
                    "Supports .csv and .xlsx files",
                    font_size="2",
                    color=rx.color("gray", 10),
                ),
                align="center",
                spacing="2",
                padding="6",
            ),
            id="upload_section",
            multiple=True,
            accept={
                "text/csv": [".csv"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
                    ".xlsx"
                ],
            },
            border=f"2px dashed {rx.color('accent', 6)}",
            border_radius="xl",
            background_color=rx.color("accent", 2),
            _hover={"cursor": "pointer"},
            on_drop=FileInputState.upload_files(
                rx.upload_files_chunk(upload_id="upload_section")
            ),
            width="100%",
        ),
        # Action Bar
        rx.hstack(
            rx.text(
                f"Files Ready ({FileInputState.get_uploaded_files.length()})",
                font_weight="bold",
                font_size="3",
            ),
            rx.spacer(),
            rx.button(
                "Clear All",
                _hover={"cursor": "pointer"},
                variant="soft",
                color_scheme="gray",
                on_click=FileInputState.clear_all_files,
                is_disabled=FileInputState.get_uploaded_files.length() == 0,
            ),
            rx.button(
                "Dump Files",
                _hover={"cursor": "pointer"},
                icon="arrow-up-from-line",
                on_click=FileInputState.dump_files,
                loading=FileInputState.is_uploading,
                is_disabled=FileInputState.get_uploaded_files.length() == 0,
                color_scheme="blue",
            ),
            width="100%",
            align="center",
            padding_y="2",
        ),
        # File Cards List
        rx.vstack(
            rx.foreach(
                FileInputState.get_uploaded_files,
                lambda filename: uploaded_file_card(filename),
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        spacing="4",
        max_width="700px",
        margin="0 auto",
    )


def uploaded_file_card(filename: rx.Var[str]) -> rx.Component:
    is_selected = FileInputState.selected_file == filename

    return rx.card(
        rx.vstack(
            # Card Header
            rx.hstack(
                rx.hstack(
                    rx.icon("file-text", color=rx.color("blue", 9), size=20),
                    rx.text(filename, font_weight="semibold", font_size="3"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.hstack(
                    # Dynamic badge based on file extension
                    rx.cond(
                        filename.contains(".xlsx"),
                        rx.badge("XLSX", color_scheme="green", variant="soft"),
                        rx.badge("CSV", color_scheme="blue", variant="soft"),
                    ),
                    rx.button(
                        rx.icon(
                            rx.cond(is_selected, "chevron-up", "chevron-down"),
                            size=18,
                        ),
                        _hover={"cursor": "pointer"},
                        variant="ghost",
                        size="1",
                        on_click=FileInputState.select_file(filename),
                    ),
                    rx.button(
                        rx.icon("trash-2", size=18, color=rx.color("red", 9)),
                        _hover={"cursor": "pointer"},
                        variant="ghost",
                        size="1",
                        color_scheme="red",
                        on_click=FileInputState.remove_file(filename),
                    ),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                align="center",
            ),
            # Collapsible Column Mapping Interface
            rx.cond(
                is_selected,
                rx.vstack(
                    rx.divider(margin_y="2"),
                    rx.hstack(
                        rx.text(
                            "Source File Column",
                            font_weight="bold",
                            font_size="2",
                            width="45%",
                        ),
                        rx.icon("arrow-right", size=14, color=rx.color("gray", 8)),
                        rx.text(
                            "Target DB Column",
                            font_weight="bold",
                            font_size="2",
                            width="45%",
                        ),
                        width="100%",
                        align="center",
                        padding_x="2",
                    ),
                    rx.foreach(
                        FileInputState.file_columns[filename],
                        lambda col: column_mapping_row(filename, col),
                    ),
                    width="100%",
                    spacing="2",
                    padding_top="2",
                ),
            ),
            width="100%",
        ),
        width="100%",
        variant="classic",
        style={
            "_hover": {"border_color": rx.color("accent", 7)},
            "transition": "all 0.2s ease",
        },
    )


def column_mapping_row(filename: rx.Var[str], col: rx.Var[str]) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.code(col, variant="soft", color_scheme="gray"),
            width="45%",
        ),
        rx.icon("arrow-right", size=14, color=rx.color("gray", 8)),
        rx.box(
            rx.input(
                placeholder="Target column name...",
                on_change=lambda val: FileInputState.update_mapping(filename, col, val),
                size="1",
                variant="surface",
            ),
            width="45%",
        ),
        width="100%",
        align="center",
        padding_x="2",
    )

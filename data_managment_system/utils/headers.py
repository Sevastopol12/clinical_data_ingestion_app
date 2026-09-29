import csv
import logging
from io import BytesIO, StringIO

from openpyxl import load_workbook

logger = logging.getLogger(__name__)


def extract_csv_excel_headers(filename: str, content: bytes) -> list[str]:
    """Extracts column headers from either CSV or XLSX bytes."""
    try:
        normalized_filename = filename.lower()
        if normalized_filename.endswith(".xlsx"):
            excel_file = BytesIO(content)
            wb = load_workbook(excel_file, read_only=True, data_only=True)
            sheet = wb.active
            if sheet is None:
                return []
            first_row = next(sheet.iter_rows(values_only=True), [])
            return [str(cell) for cell in first_row if cell is not None]

        elif normalized_filename.endswith(".csv"):
            text_stream = StringIO(content.decode("utf-8-sig", errors="ignore"))
            reader = csv.reader(text_stream)
            return next(reader, [])

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to extract headers for %s: %s", filename, exc)

    return []


__all__ = ["extract_csv_excel_headers"]

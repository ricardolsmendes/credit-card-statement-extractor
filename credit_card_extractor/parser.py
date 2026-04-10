from collections import defaultdict
from pathlib import Path
from typing import Iterator

import pdfplumber

# Table extraction settings — tries drawn lines first (most reliable for bank PDFs)
_TABLE_SETTINGS_LINES: dict = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
}

_TABLE_SETTINGS_TEXT: dict = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "snap_tolerance": 3,
    "join_tolerance": 3,
}

# Tolerance in points for grouping words on the same line (by top coordinate)
_LINE_TOP_TOLERANCE = 3.0
# Gap threshold for detecting column boundaries from word x0 positions
_COLUMN_GAP_THRESHOLD = 20.0


def _tables_to_rows(tables: list[list[list[str | None]]]) -> list[list[str]]:
    """Flatten extracted tables into a single list of string rows."""
    rows: list[list[str]] = []
    for table in tables:
        for row in table:
            if row is not None:
                rows.append([cell or "" for cell in row])
    return rows


def _word_bbox_rows(page: pdfplumber.page.Page) -> list[list[str]]:
    """
    Fallback column inference from word bounding boxes.

    1. Extract words with x0, top coordinates.
    2. Group words into logical lines by top coordinate (within tolerance).
    3. Cluster x0 positions to identify column boundaries.
    4. Assign each word to the nearest column bucket.
    5. Return rows as lists of per-column joined strings.
    """
    words = page.extract_words()
    if not words:
        return []

    # Group words by line (cluster by top coordinate)
    lines: dict[float, list[dict]] = {}
    for word in words:
        top = word["top"]
        matched_top = None
        for existing_top in lines:
            if abs(existing_top - top) <= _LINE_TOP_TOLERANCE:
                matched_top = existing_top
                break
        if matched_top is None:
            matched_top = top
        lines.setdefault(matched_top, []).append(word)

    if not lines:
        return []

    # Collect all first-word x0 positions per line to infer column boundaries
    all_x0 = sorted({w["x0"] for line_words in lines.values() for w in line_words})

    # Cluster x0 values: a new cluster starts when gap > threshold
    column_boundaries: list[float] = []
    if all_x0:
        column_boundaries.append(all_x0[0])
        for x in all_x0[1:]:
            if x - column_boundaries[-1] > _COLUMN_GAP_THRESHOLD:
                column_boundaries.append(x)

    def assign_column(x0: float) -> int:
        """Return index of the nearest column boundary."""
        return min(range(len(column_boundaries)), key=lambda i: abs(column_boundaries[i] - x0))

    # Build rows
    rows: list[list[str]] = []
    for top in sorted(lines.keys()):
        line_words = sorted(lines[top], key=lambda w: w["x0"])
        cols: dict[int, list[str]] = defaultdict(list)
        for word in line_words:
            col_idx = assign_column(word["x0"])
            cols[col_idx].append(word["text"])

        num_cols = len(column_boundaries)
        row = [" ".join(cols.get(i, [])) for i in range(num_cols)]
        rows.append(row)

    return rows


def extract_raw_rows_from_page(page: pdfplumber.page.Page) -> list[list[str]]:
    """
    Attempt table extraction using multiple strategies in priority order:
    1. Lines strategy (drawn PDF lines)
    2. Text strategy (column-aligned text)
    3. Word bounding-box column inference (last resort)

    Returns a flat list of rows from all tables found on the page.
    """
    # Strategy 1: lines
    tables = page.extract_tables(table_settings=_TABLE_SETTINGS_LINES)
    rows = _tables_to_rows(tables)
    if rows:
        return rows

    # Strategy 2: text-based
    tables = page.extract_tables(table_settings=_TABLE_SETTINGS_TEXT)
    rows = _tables_to_rows(tables)
    if rows:
        return rows

    # Strategy 3: word bbox fallback
    return _word_bbox_rows(page)


def extract_raw_rows(pdf_path: Path) -> Iterator[tuple[int, list[list[str]]]]:
    """
    Open PDF and yield (1-based page_number, rows) for each page that has content.
    """
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            rows = extract_raw_rows_from_page(page)
            if rows:
                yield page_num, rows

from pathlib import Path

from credit_card_extractor.heuristics import (
    RowClass,
    classify_row,
    infer_column_indices,
    is_header_row,
)
from credit_card_extractor.models import ExtractionResult, Transaction
from credit_card_extractor.normalizer import normalize_description, parse_amount, parse_date
from credit_card_extractor.parser import extract_raw_rows


def extract(pdf_path: Path, verbose: bool = False) -> ExtractionResult:
    """
    Main extraction pipeline.

    For each page:
    1. Get raw rows from parser.
    2. Detect header row to infer column indices.
    3. Classify each row.
    4. TRANSACTION  → build Transaction, append to list.
    5. CONTINUATION → append text to the last Transaction's description.
    6. HEADER/NOISE → skip.
    7. Rows with a date but unparseable amount → record warning.
    """
    transactions: list[Transaction] = []
    warnings: list[str] = []
    pages_processed = 0
    col_indices: dict[str, int] | None = None

    for page_num, rows in extract_raw_rows(pdf_path):
        pages_processed += 1

        for row in rows:
            if is_header_row(row):
                col_indices = infer_column_indices(row)
                continue

            classification = classify_row(row, col_indices=col_indices)

            if classification == RowClass.TRANSACTION:
                t = _build_transaction(row, col_indices, page_num, warnings)
                if t is not None:
                    transactions.append(t)

            elif classification == RowClass.CONTINUATION:
                if transactions:
                    continuation_text = " ".join(c for c in row if c and c.strip())
                    combined = transactions[-1].description + " " + continuation_text
                    transactions[-1].description = normalize_description(combined)

    return ExtractionResult(
        transactions=transactions,
        warnings=warnings,
        source_file=str(pdf_path),
        pages_processed=pages_processed,
    )


def _build_transaction(
    row: list[str],
    col_indices: dict[str, int] | None,
    page_num: int,
    warnings: list[str],
) -> Transaction | None:
    """
    Extract and normalize fields from a classified TRANSACTION row.
    Returns None and appends to warnings if critical fields (date or amount) fail.
    """
    num_cols = len(row)

    if col_indices and num_cols > max(col_indices.values(), default=0):
        date_cell = row[col_indices.get("date", 0)]
        amount_idx = col_indices.get("amount", num_cols - 1)
        amount_cell = row[amount_idx] if amount_idx < num_cols else ""
        desc_idx = col_indices.get("description", 1 if num_cols > 2 else 0)
        desc_cell = row[desc_idx] if desc_idx < num_cols else ""
        ref_idx = col_indices.get("reference")
        ref_cell = row[ref_idx] if ref_idx is not None and ref_idx < num_cols else ""
        cat_idx = col_indices.get("category")
        cat_cell = row[cat_idx] if cat_idx is not None and cat_idx < num_cols else ""
    else:
        date_cell = row[0] if row else ""
        amount_cell = row[-1] if len(row) > 1 else ""
        desc_cell = row[1] if len(row) > 2 else ""
        ref_cell = ""
        cat_cell = ""

    parsed_date = parse_date(date_cell)
    if parsed_date is None:
        warnings.append(
            f"Page {page_num}: could not parse date '{date_cell}' in row: {row}"
        )
        return None

    parsed_amount = parse_amount(amount_cell)
    if parsed_amount is None:
        warnings.append(
            f"Page {page_num}: could not parse amount '{amount_cell}' in row: {row}"
        )
        return None

    return Transaction(
        date=parsed_date,
        description=normalize_description(desc_cell),
        amount=parsed_amount,
        original_amount_str=amount_cell.strip(),
        reference=normalize_description(ref_cell),
        category=normalize_description(cat_cell),
        page_number=page_num,
    )

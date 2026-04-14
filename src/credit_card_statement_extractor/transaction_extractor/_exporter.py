"""Exporter — writes transactions to CSV or XLSX files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from credit_card_statement_extractor.transaction_extractor._locale import LocaleConfig
    from credit_card_statement_extractor.transaction_extractor._models import Transaction


class Exporter:
    """Writes a list of transactions to a CSV or XLSX file."""

    def export(
        self,
        transactions: list[Transaction],
        locale: LocaleConfig,
        path: Path,
        fmt: Literal["csv", "xlsx"],
        has_beneficiary: bool = False,
    ) -> None:
        """Write *transactions* to *path* in the given *fmt* format.

        Args:
            transactions: Parsed transactions to export.
            locale: Locale configuration (controls headers and date format).
            path: Destination file path.
            fmt: Export format — ``"csv"`` or ``"xlsx"``.
            has_beneficiary: When True, include a beneficiary column.

        Raises:
            OSError: If the file cannot be written.
            RuntimeError: If ``fmt=="xlsx"`` and xlsxwriter is not installed.
            ValueError: If *fmt* is not ``"csv"`` or ``"xlsx"``.
        """
        if fmt == "csv":
            self._write_csv(transactions, locale, path, has_beneficiary)
        elif fmt == "xlsx":
            self._write_xlsx(transactions, locale, path, has_beneficiary)
        else:
            raise ValueError(f"Unsupported format: {fmt!r}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _write_csv(
        self,
        transactions: list[Transaction],
        locale: LocaleConfig,
        path: Path,
        has_beneficiary: bool,
    ) -> None:
        header = self._build_header(locale, has_beneficiary)
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            for txn in transactions:
                row = [txn.date.strftime(locale.date_format)]
                if has_beneficiary:
                    row.append(txn.beneficiary or "")
                row.append(txn.description)
                row.append(str(txn.amount))
                writer.writerow(row)

    def _write_xlsx(
        self,
        transactions: list[Transaction],
        locale: LocaleConfig,
        path: Path,
        has_beneficiary: bool,
    ) -> None:
        try:
            import xlsxwriter  # noqa: PLC0415
        except (ImportError, TypeError):
            raise RuntimeError(
                "XLSX export requires xlsxwriter. Install it with: pip install xlsxwriter"
            )

        workbook = xlsxwriter.Workbook(str(path), {"remove_timezone": True})
        worksheet = workbook.add_worksheet("Transactions")
        bold = workbook.add_format({"bold": True})
        date_fmt = workbook.add_format({"num_format": "dd/mm/yyyy"})
        num_fmt = workbook.add_format({"num_format": "#,##0.00"})

        header = self._build_header(locale, has_beneficiary)
        for col, label in enumerate(header):
            worksheet.write(0, col, label, bold)

        for row_idx, txn in enumerate(transactions, start=1):
            col = 0
            worksheet.write_datetime(row_idx, col, txn.date, date_fmt)
            col += 1
            if has_beneficiary:
                worksheet.write(row_idx, col, txn.beneficiary or "")
                col += 1
            worksheet.write(row_idx, col, txn.description)
            col += 1
            worksheet.write_number(row_idx, col, float(txn.amount), num_fmt)

        workbook.close()

    @staticmethod
    def _build_header(locale: LocaleConfig, has_beneficiary: bool) -> list[str]:
        header = [locale.col_date]
        if has_beneficiary:
            header.append(locale.col_beneficiary)
        header.append(locale.col_description)
        header.append(locale.col_amount)
        return header

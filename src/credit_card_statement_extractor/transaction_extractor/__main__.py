"""CLI entry point for the transaction extractor.

Usage:
    python -m credit_card_statement_extractor.transaction_extractor <file_path>
        [--lang en|pt-BR] [--output-format csv|xlsx]

Exit codes:
    0 — success (at least one transaction extracted)
    1 — user error (no argument, file not found, or export write error)
    2 — parse failure (not a valid PDF, or no transactions found)
    3 — unexpected internal error
"""

import argparse
import sys
from pathlib import Path

from credit_card_statement_extractor.pdf_reader._pdfplumber_reader import (
    PdfplumberReader,
)
from credit_card_statement_extractor.transaction_extractor._exporter import Exporter
from credit_card_statement_extractor.transaction_extractor._formatter import Formatter
from credit_card_statement_extractor.transaction_extractor._locale import (
    LOCALE_EN,
    LOCALE_PT_BR,
)
from credit_card_statement_extractor.transaction_extractor._parser import DefaultParser

_USAGE = (
    "Usage: python -m credit_card_statement_extractor.transaction_extractor"
    " <file_path> [--lang <code>] [--output-format csv|xlsx]"
)

_LOCALES = {
    "en": LOCALE_EN,
    "pt-BR": LOCALE_PT_BR,
}


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="credit_card_statement_extractor.transaction_extractor",
        description="Extract and display transactions from a credit card statement PDF.",
        add_help=True,
    )
    parser.add_argument(
        "file_path",
        help="Path to the PDF credit card statement.",
    )
    parser.add_argument(
        "--lang",
        choices=list(_LOCALES.keys()),
        default="en",
        help="Output language (default: en).",
    )
    parser.add_argument(
        "--output-format",
        choices=["csv", "xlsx"],
        default=None,
        help="Export transactions to a file instead of printing to stdout.",
    )
    return parser


def main() -> None:
    # Handle no-argument case before argparse to control exit code and message.
    if len(sys.argv) < 2:
        print(_USAGE, file=sys.stderr)
        sys.exit(1)

    arg_parser = _build_arg_parser()

    try:
        args = arg_parser.parse_args()
    except SystemExit:
        sys.exit(1)

    path = Path(args.file_path)
    locale = _LOCALES[args.lang]

    try:
        reader = PdfplumberReader()
        pages = reader.read(path)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print(f"Error: Could not parse as PDF: {path}", file=sys.stderr)
        sys.exit(2)
    except Exception:
        print(
            "Error: An unexpected error occurred. Please report this issue.",
            file=sys.stderr,
        )
        sys.exit(3)

    try:
        parser = DefaultParser()
        transactions, skipped = parser.parse(pages)
    except ValueError:
        print(f"Error: No transactions found in {path}", file=sys.stderr)
        sys.exit(2)
    except Exception:
        print(
            "Error: An unexpected error occurred. Please report this issue.",
            file=sys.stderr,
        )
        sys.exit(3)

    if not transactions:
        print(f"Error: No transactions found in {path}", file=sys.stderr)
        sys.exit(2)

    if skipped > 0:
        print(
            f"Warning: {skipped} line(s) could not be parsed and were skipped.",
            file=sys.stderr,
        )

    has_beneficiary = any(t.beneficiary is not None for t in transactions)

    if args.output_format is not None:
        output_path = Path(args.file_path).resolve().parent / (
            Path(args.file_path).stem + f"-transactions.{args.output_format}"
        )
        try:
            Exporter().export(
                transactions,
                locale,
                output_path,
                args.output_format,
                has_beneficiary=has_beneficiary,
            )
        except (OSError, PermissionError) as e:
            print(f"Error: Cannot write to output file: {output_path}\n{e}", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"Exported {len(transactions)} transactions to {output_path.name}")
    else:
        formatter = Formatter()
        print(formatter.render(transactions, locale, has_beneficiary=has_beneficiary))


if __name__ == "__main__":
    main()

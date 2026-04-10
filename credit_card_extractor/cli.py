from pathlib import Path
from typing import Optional

import typer

from credit_card_extractor.exporters import export_csv, export_xlsx
from credit_card_extractor.extractor import extract
from credit_card_extractor.i18n import Language

app = typer.Typer(
    name="ccextract",
    help="Extract credit card statement transactions from PDF files.",
    no_args_is_help=True,
)


@app.command(name="extract")
def extract_cmd(
    pdf_file: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        resolve_path=True,
        help="Path to the PDF statement file.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. Format is inferred from extension if provided.",
    ),
    format: str = typer.Option(
        "csv",
        "--format",
        "-f",
        help="Output format: csv or xlsx.",
    ),
    language: Language = typer.Option(
        Language.EN,
        "--language",
        "-l",
        help="Language for output column headers.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print extraction details to stderr.",
    ),
) -> None:
    """Extract transactions from PDF_FILE and export to CSV or Excel."""
    # Infer format from output extension if --output is given
    if output is not None:
        suffix = output.suffix.lower()
        if suffix == ".xlsx":
            format = "xlsx"
        elif suffix == ".csv":
            format = "csv"
    else:
        ext = "xlsx" if format == "xlsx" else "csv"
        output = pdf_file.with_suffix(f".{ext}")

    if format not in ("csv", "xlsx"):
        typer.echo(f"Error: unsupported format '{format}'. Use 'csv' or 'xlsx'.", err=True)
        raise typer.Exit(code=1)

    result = extract(pdf_file, verbose=verbose)

    if verbose:
        typer.echo(f"Processed {result.pages_processed} page(s)", err=True)
        typer.echo(f"Found {len(result.transactions)} transaction(s)", err=True)
        for w in result.warnings:
            typer.echo(f"  Warning: {w}", err=True)

    if format == "xlsx":
        export_xlsx(result, output, language=language)
    else:
        export_csv(result, output, language=language)

    typer.echo(f"Exported {len(result.transactions)} transaction(s) to {output}")

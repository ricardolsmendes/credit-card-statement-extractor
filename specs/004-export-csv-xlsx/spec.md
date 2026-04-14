# Feature Specification: Export Transactions to CSV and XLSX

**Feature Branch**: `004-export-csv-xlsx`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: User description: "Now that the application is able to parse and extract transaction data, it's time to improve it with the export CSV and XLSX capability."

## Clarifications

### Session 2026-04-14

- Q: How should the output flag work and how should the output file be named? → A: The flag is `--output-format` accepting `csv` or `xlsx`. The output file name is derived from the input PDF file name: `<input_stem>-transactions.<ext>` (e.g., `statement-transactions.csv` for `statement.pdf`). The file is written to the same directory as the input PDF.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Export Transactions to CSV (Priority: P1)

A user has a credit card PDF statement and wants to export the extracted transactions to a CSV file so they can open it in a spreadsheet application (e.g., Excel, Google Sheets, LibreOffice Calc) or process it with other tools.

**Why this priority**: CSV is the most universal, lightweight export format. It works with every spreadsheet tool and can be imported into budgeting apps, databases, or scripts. It delivers immediate value as the baseline export capability and requires no additional dependencies.

**Independent Test**: Run the CLI with `--output-format csv` on a known PDF statement (e.g., `statement.pdf`) and verify that a file named `statement-transactions.csv` is created in the same directory, containing the correct headers and all transaction rows with properly formatted values.

**Acceptance Scenarios**:

1. **Given** a valid PDF `statement.pdf` with 4 transactions, **When** the user runs the CLI with `--output-format csv`, **Then** a file `statement-transactions.csv` is created in the same directory as the PDF, containing one header row and four data rows, with columns for date, description, and amount.
2. **Given** a PDF statement with a `Beneficiário` column, **When** the user exports with `--output-format csv`, **Then** the CSV includes a beneficiary column between date and description.
3. **Given** a valid PDF statement, **When** the user runs the CLI with `--output-format csv --lang pt-BR`, **Then** the CSV uses pt-BR column labels ("Data", "Descrição", "Valor") and date format DD/MM/YYYY.
4. **Given** a CSV file with the derived name already exists, **When** the CLI runs, **Then** the existing file is silently overwritten.
5. **Given** a CSV file is successfully written, **When** the user opens it in a spreadsheet application, **Then** each transaction appears on its own row with values correctly separated and no data corruption.

---

### User Story 2 — Export Transactions to XLSX (Priority: P2)

A user wants to export extracted transactions to an Excel-compatible XLSX file, so that they can benefit from spreadsheet formatting — column widths, number formatting, and direct compatibility with Microsoft Excel and similar tools.

**Why this priority**: XLSX is the de facto standard for structured financial data exchange and is required by many finance and accounting workflows. It builds on the CSV export foundation and adds value for users who work primarily in Excel.

**Independent Test**: Run the CLI with `--output-format xlsx` on a known PDF statement (e.g., `statement.pdf`) and verify that a file named `statement-transactions.xlsx` is created in the same directory, openable in a spreadsheet application with correct data types (dates as dates, amounts as numbers).

**Acceptance Scenarios**:

1. **Given** a valid PDF `statement.pdf`, **When** the user runs the CLI with `--output-format xlsx`, **Then** a file `statement-transactions.xlsx` is created in the same directory as the PDF, with one header row and one row per transaction.
2. **Given** an XLSX export, **When** the user opens it, **Then** date values are stored as proper date types and amount values as numeric types (not plain text strings).
3. **Given** a PDF statement with a `Beneficiário` column, **When** the user exports with `--output-format xlsx`, **Then** the XLSX includes a beneficiary column in the same position as in the CSV export.
4. **Given** the user specifies `--output-format xlsx --lang pt-BR`, **Then** the XLSX uses pt-BR column labels and date format.
5. **Given** an XLSX file with the derived name already exists, **When** the CLI runs, **Then** the existing file is overwritten without prompting.

---

### Edge Cases

- How does the export handle transactions with special characters (accents, asterisks, slashes) in descriptions?
- What happens when the amount is a very large number that could cause precision loss in a spreadsheet?
- What if the PDF yields zero transactions? No export file is created; the existing "No transactions found" error path fires.
- What if the user does not have write permission to the directory containing the input PDF? An error is printed to stderr and the process exits with a non-zero code.
- What if `--output-format xlsx` is requested but the XLSX library is not installed? A clear error with install instructions is shown on stderr.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST accept an `--output-format` argument with allowed values `csv` and `xlsx`.
- **FR-002**: When `--output-format csv` is given, the system MUST write a valid RFC 4180 CSV file named `<input_stem>-transactions.csv` in the same directory as the input PDF.
- **FR-003**: When `--output-format xlsx` is given, the system MUST write a valid XLSX file named `<input_stem>-transactions.xlsx` in the same directory as the input PDF.
- **FR-004**: CSV and XLSX column order MUST be: Date, Beneficiary (only if present), Description, Amount.
- **FR-005**: CSV and XLSX column labels MUST use the locale specified by `--lang` (default: English).
- **FR-006**: Date values in CSV MUST be formatted as text using the locale's date format string (e.g., `2026-03-01` for English, `01/03/2026` for pt-BR).
- **FR-007**: Date values in XLSX MUST be stored as native date types.
- **FR-008**: Amount values in CSV MUST be written as plain numeric strings without currency symbols or thousands separators (e.g., `-4.50`, `500.00`), to ensure interoperability with spreadsheet import.
- **FR-009**: Amount values in XLSX MUST be stored as native numeric types.
- **FR-010**: If the output file cannot be written (permission error, non-writable directory, etc.), the system MUST print an error message to stderr and exit with code 1.
- **FR-011**: If `--output-format` is omitted, behaviour MUST remain unchanged — the system prints the formatted table to stdout as before.
- **FR-012**: When an XLSX or CSV file is successfully written, the system MUST print a confirmation message to stdout (e.g., `Exported 4 transactions to statement-transactions.csv`).
- **FR-013**: If the PDF yields zero transactions (error condition), no output file MUST be written.
- **FR-014**: If `--output-format xlsx` is requested but the XLSX library is not installed, the system MUST print an error to stderr with installation instructions and exit with code 1.

### Key Entities

- **ExportFile**: The output artifact — a CSV or XLSX file whose name is derived from the input PDF stem, containing transaction data with locale-appropriate headers and formatting.
- **Transaction** (existing): Date, description, optional beneficiary, amount — the data written to each row.
- **LocaleConfig** (existing): Controls column labels and date format in the export output.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A CSV or XLSX export of a 4-transaction statement completes in under 5 seconds end-to-end (including PDF parsing).
- **SC-002**: Exported CSV files open without errors or encoding warnings in at least three major spreadsheet tools (Excel, Google Sheets, LibreOffice Calc).
- **SC-003**: Exported XLSX files contain correct native data types — dates and amounts are not stored as plain text.
- **SC-004**: All transaction data is preserved in the export with no loss of precision for amounts (no rounding errors or truncation).
- **SC-005**: The `--output-format` flag integrates into the existing CLI without breaking any current behaviour (all existing tests continue to pass).

## Assumptions

- The user runs the CLI from a shell where they have write permissions to the directory containing the input PDF.
- If the derived output file already exists, it is silently overwritten — no conflict resolution or backup is needed.
- XLSX export requires an additional dependency (a pure-Python XLSX writer library); this is acceptable as an opt-in extra.
- CSV output uses UTF-8 encoding with a BOM (Byte Order Mark) to ensure correct display in Excel on Windows.
- The beneficiary column is included in the export only when at least one transaction in the statement has a non-null beneficiary value (same logic as the existing table formatter).
- When `--output-format` is given, only the confirmation message is written to stdout; the table is suppressed.
- Empty files (zero transactions) are not written; the existing "No transactions found" error path already handles this.

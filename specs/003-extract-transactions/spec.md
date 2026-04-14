# Feature Specification: Transaction Extractor

**Feature Branch**: `003-extract-transactions`  
**Created**: 2026-04-12  
**Status**: Clarified (2026-04-14)  
**Input**: User description: "Once the pdf_reader module is able to read a sample credit card statement provided by the user, it's time to build meaningful features on top of it. The first one consists of extracting transactions data from the raw output and printing results in the console. The application must provide multi language support, starting with English and Brazilian Portuguese. Finally, there is no need to build a complex CLI interface at this point; reading the input file name from the main Python command and printing the reading results in the console is enough for now."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract and Display Transactions from a Statement (Priority: P1)

A developer provides a credit card statement PDF file as a command-line argument. The application reads the file, identifies the individual transaction lines, and prints a structured list of transactions to the console — each showing the date, description, and amount. This allows the developer to verify that meaningful transaction data is being extracted from the raw PDF content.

**Why this priority**: This is the core value of the entire application. Without the ability to extract structured transaction data, no downstream processing (reporting, categorisation, export) is possible. Every other feature builds on this foundation.

**Independent Test**: Run `python -m <module> statement.pdf` with a known statement PDF. Confirm the output contains a visible list of individual transactions with recognisable dates, descriptions, and amounts. Confirm the transaction count matches the number of entries visible in the original PDF.

**Acceptance Scenarios**:

1. **Given** a valid credit card statement PDF, **When** the user runs the application with that file path, **Then** a formatted list of transactions is printed to stdout, each line showing date, description, and amount; when a beneficiary column is present in the statement, it is shown as an additional column in the output.
2. **Given** a statement with multiple transactions, **When** the application processes it, **Then** all transactions appear in the output in the same order they appear in the statement.
3. **Given** a statement that contains both purchases and payments/credits, **When** the application processes it, **Then** all transaction types are included in the output, with credit amounts clearly distinguished from debit amounts.
4. **Given** a Brazilian Portuguese statement where transaction dates are written in long format (e.g., "14 de mar. 2026"), **When** the application processes it, **Then** all such transactions are correctly extracted and their dates are displayed in the output date format for the selected locale.

---

### User Story 2 - View Output in a Selected Language (Priority: P2)

A developer wants to see transaction output formatted according to their locale. They can specify the display language when running the application. Column labels, messages, and number/date formatting follow the selected locale. When no language is specified, English is used by default.

**Why this priority**: Multi-language support is explicitly required and directly affects the usability of the output for Brazilian Portuguese speakers. Amount formatting in particular (R$ 1.234,56 vs $1,234.56) is crucial for correct human interpretation.

**Independent Test**: Run the application with a language option set to Brazilian Portuguese and confirm that (a) column headers appear in Portuguese, (b) amounts are formatted with comma as the decimal separator and the R$ currency prefix, and (c) dates are formatted in the dd/mm/yyyy convention.

**Acceptance Scenarios**:

1. **Given** the user runs the application without specifying a language, **When** transactions are printed, **Then** output labels and formatting follow English conventions.
2. **Given** the user specifies Brazilian Portuguese as the output language, **When** transactions are printed, **Then** column labels appear in Portuguese, amounts use R$ with comma-decimal formatting, and dates use dd/mm/yyyy.
3. **Given** the user specifies English as the output language, **When** transactions are printed, **Then** column labels appear in English, amounts use standard English number formatting, and dates use YYYY-MM-DD format.

---

### User Story 3 - Graceful Handling of Unrecognised or Empty Statements (Priority: P3)

A developer runs the application with a PDF whose transaction layout cannot be parsed — either because the format is unrecognised or the page contains no transaction data. The application does not crash; instead it prints a clear, informative message describing the problem.

**Why this priority**: Robustness against unexpected input is essential for a tool intended to handle real-world PDFs from different banks and layouts.

**Independent Test**: Run the application with a PDF that contains no recognisable transaction lines. Confirm a human-readable message is printed to stderr and the application exits with a non-zero code. Confirm stdout contains no partial or malformed transaction data.

**Acceptance Scenarios**:

1. **Given** a PDF with no recognisable transaction data, **When** the user runs the application, **Then** a message stating that no transactions were found is printed to stderr and the application exits with a non-zero code.
2. **Given** a PDF where only some transaction lines are recognisable, **When** the user runs the application, **Then** only the successfully parsed transactions are printed to stdout, with a warning on stderr indicating how many lines could not be parsed.

---

### Edge Cases

- What happens when a transaction amount is negative (refund or credit)?
- What happens when a transaction description contains special characters or is unusually long?
- What happens when the statement spans multiple pages and transactions are split across them?
- What happens when two transactions share the same date and description?
- What happens when the PDF has no text layer (scanned image)?
- What happens when a pt-BR long date uses a month abbreviation without a trailing period (e.g., "14 de mar 2026" vs "14 de mar. 2026")?
- What happens when the statement mixes numeric and long date formats on the same page?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST accept a PDF file path as a command-line argument.
- **FR-002**: The application MUST use the existing PDF reader module to extract raw text from the provided file.
- **FR-003**: The application MUST parse individual transactions from the extracted text, identifying at minimum: transaction date, description, and amount. When detecting the transaction table in Brazilian Portuguese statements, the parser MUST recognise the following column header variants — date: "Data", "Data da Compra", "Data Lançamento"; description: "Descrição", "Histórico", "Movimentação", "Estabelecimento"; amount: "Valor", "Valor (R$)".
- **FR-004**: The application MUST print the list of extracted transactions to standard output as a fixed-width table with aligned columns, a header row, and a separator line beneath the header. When a beneficiary column was present in the source statement, the output table MUST include it as an additional column; otherwise the column is omitted.
- **FR-005**: The application MUST preserve the original ordering of transactions as they appear in the statement.
- **FR-006**: The application MUST support English and Brazilian Portuguese as output languages.
- **FR-007**: The application MUST accept an optional language argument, defaulting to English when not specified.
- **FR-008**: The application MUST format amounts and dates according to the conventions of the selected output language. English date format: YYYY-MM-DD. Brazilian Portuguese date format: DD/MM/YYYY. Negative amounts use a leading minus sign in both locales.
- **FR-009**: The application MUST display column labels in the selected output language. For English: "Date", "Description", "Amount" (plus "Beneficiary" when the column is present). For Brazilian Portuguese: "Data", "Descrição", "Valor" (plus "Beneficiário" when the column is present).
- **FR-010**: The application MUST print a clear error message to stderr and exit with a non-zero code when no transactions can be extracted.
- **FR-011**: The application MUST print a warning to stderr and continue when some transaction lines cannot be parsed, displaying the successfully extracted transactions.
- **FR-012**: The application MUST exit with a non-zero status code when a fatal error occurs.
- **FR-013**: The parser MUST recognise transaction dates expressed in the Brazilian Portuguese long format "DD de MMM. YYYY" (e.g., "14 de mar. 2026"), where the month abbreviation follows standard pt-BR three-letter month abbreviations (jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez), with or without a trailing period.
- **FR-014**: The parser MUST recognise "Beneficiário" as an optional, distinct column in the transaction table — separate from the description column. When present, its value MUST be captured per transaction. When absent, the beneficiary attribute for each transaction is empty.

### Key Entities

- **Transaction**: A single financial event on the statement. Key attributes: date, description, amount (positive for purchases/charges, negative for payments/credits), beneficiary (optional — present only when the source statement includes a "Beneficiário" column).
- **Statement**: The PDF document provided as input; produces a list of Transactions when parsed.
- **Locale**: The display configuration selected by the user (language, number format, date format, currency symbol).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can run a single command and view all transactions from a real credit card statement within 10 seconds, regardless of statement size up to 50 pages.
- **SC-002**: Every transaction visible in the source PDF appears exactly once in the output — no duplicates and no omissions for recognised transaction lines.
- **SC-003**: Switching the output language (English ↔ Brazilian Portuguese) changes the display format without requiring code changes — a single user-facing option controls all locale-specific formatting.
- **SC-004**: The application never exposes raw tracebacks to the user; every failure produces a distinct, actionable error message.

## Clarifications

### Session 2026-04-12

- Q: What are the exact column header labels for Date, Description, and Amount in Brazilian Portuguese? → A: Data / Descrição / Valor
- Q: What output format should transactions use when printed to stdout? → A: Fixed-width aligned columns with a header row and separator line.
- Q: What date format should be used for English output? → A: YYYY-MM-DD (ISO 8601).
- Q: How should negative amounts (credits, refunds, payments) be displayed? → A: Minus sign prefix for both locales (e.g., -R$ 1.234,56 / -1,234.56).
- Q: Which Brazilian Portuguese description column header variants should the parser recognise? → A: Descrição, Histórico, Movimentação, Estabelecimento (4 variants).
- Q: Which Brazilian Portuguese amount column header variants should the parser recognise? → A: Valor, Valor (R$) (2 variants).
- Q: Which Brazilian Portuguese date column header variants should the parser recognise? → A: Data, Data da Compra, Data Lançamento (3 variants).

### Session 2026-04-14 (implementation feedback)

- Finding: The real statement uses pt-BR long date format "14 de mar. 2026" rather than numeric DD/MM/YYYY. The original spec and implementation only handled numeric date formats; FR-013 added to explicitly require support for this long format.
- Finding: Month abbreviations in the observed statement do not include a trailing period consistently; FR-013 requires the parser to handle both "mar." and "mar" forms.
- Q: Is "Beneficiário" a synonym for the description column or a separate column? → A: It is a distinct, separate, optional column — not a description variant. FR-014 added; FR-003, FR-004, FR-009, Transaction entity, and Assumptions updated accordingly.

## Assumptions

- The initial implementation targets a single, well-defined credit card statement format (the sample statement provided by the developer). The architecture must allow additional formats to be added later without rewriting the core extraction logic.
- "Multi-language support" means localised output display (labels, number formatting, date formatting). It does not require automatic language detection from the PDF content — the user selects the language explicitly.
- The language selection is provided as a simple command-line argument (e.g., `--lang en` or `--lang pt-BR`); no configuration files or environment variables are required at this stage.
- Transactions are identified as lines containing at minimum a date pattern and a numeric amount. Lines that do not match this pattern are silently skipped with an optional warning count. The transaction table is located by detecting a header row; recognised column headers in Brazilian Portuguese are — date: "Data", "Data da Compra", "Data Lançamento"; description: "Descrição", "Histórico", "Movimentação", "Estabelecimento"; amount: "Valor", "Valor (R$)"; beneficiary (optional, distinct column): "Beneficiário".
- Brazilian Portuguese statements may express transaction dates in a long written format ("DD de MMM. YYYY", e.g., "14 de mar. 2026") rather than numeric format. The parser must handle both numeric (DD/MM/YYYY) and long written pt-BR date formats. Month abbreviations may appear with or without a trailing period.
- The currency symbol displayed is determined by the selected output language (USD/generic `$` for English, `R$` for Brazilian Portuguese), not by the source PDF content.
- Negative amounts (credits, payments, refunds) are represented as negative numbers and displayed with a leading minus sign in all locales (e.g., -R$ 1.234,56 for pt-BR, -1,234.56 for English).
- Performance is bounded by the pdf_reader module (SC-001 in feature 002); the transaction parsing step itself adds negligible time.
- This feature depends on the `pdf_reader` module (feature 002) being complete and functional.

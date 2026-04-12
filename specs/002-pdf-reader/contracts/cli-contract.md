# CLI Contract: PDF Reader Module

**Type**: Command-line interface  
**Entry point**: `python -m credit_card_statement_extractor.pdf_reader <file_path>`

---

## Invocation

```
python -m credit_card_statement_extractor.pdf_reader <file_path>
```

| Argument    | Required | Description                              |
|-------------|----------|------------------------------------------|
| `file_path` | Yes      | Path to the PDF file to read             |

---

## Exit Codes

| Code | Meaning                                      |
|------|----------------------------------------------|
| `0`  | Success — text extracted and printed         |
| `1`  | User error — missing argument, file not found|
| `2`  | Parse failure — file is not a valid PDF      |

(Aligned with Constitution §IV exit code conventions.)

---

## Standard Output (stdout)

On success, the extracted text is printed to stdout in the following format:

```
--- Page 1 ---
<extracted text for page 1>

--- Page 2 ---
<extracted text for page 2>

...
```

- One `--- Page N ---` header per page, in document order.
- Pages with no extractable text print the header followed by a blank line.
- No trailing newline after the last page is required.

---

## Standard Error (stderr)

All error messages are written to **stderr**, never stdout.

| Scenario               | Message format                                      |
|------------------------|-----------------------------------------------------|
| No argument provided   | `Usage: python -m credit_card_statement_extractor.pdf_reader <file_path>` |
| File not found         | `Error: File not found: <file_path>`               |
| Not a valid PDF        | `Error: Could not parse as PDF: <file_path>`       |

No raw tracebacks are printed to stderr under any circumstances.

---

## Stability

This CLI contract is the primary interface for this module. Changes to argument names, exit codes, or stdout format require a spec update. The concrete PDF library used is an internal implementation detail and is not part of this contract.

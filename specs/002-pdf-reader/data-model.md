# Data Model: PDF Reader Module

**Phase**: 1 — Design  
**Feature**: specs/002-pdf-reader  
**Date**: 2026-04-12

---

## Entities

### PageResult

Represents the extracted content of a single PDF page.

| Field         | Type   | Description                                      | Constraints                     |
|---------------|--------|--------------------------------------------------|---------------------------------|
| `page_number` | `int`  | 1-based page index                               | >= 1                            |
| `text`        | `str`  | Extracted text content for this page             | May be empty string for blank pages |

**Notes**:
- Implemented as a `dataclass` (immutable preferred: `frozen=True`).
- An empty `text` field is valid — it signals a blank or image-only page without raising an error.

---

### PDFReader (Protocol)

The swappable reader interface. Any class implementing this method is a valid reader.

| Method                              | Return type        | Description                                                  |
|-------------------------------------|--------------------|--------------------------------------------------------------|
| `read(path: Path) -> list[PageResult]` | `list[PageResult]` | Opens the PDF at `path`, extracts text page by page, returns one `PageResult` per page in document order. |

**Contract**:
- Must raise `FileNotFoundError` if `path` does not exist.
- Must raise `ValueError` if the file cannot be parsed as a PDF.
- Must never log or surface raw extracted text in error messages.
- Must iterate pages lazily where the underlying library supports it.

---

## State Transitions

The reader is stateless — each `read()` call is independent. No persistent state between invocations.

---

## Relationships

```
CLI entry point
    │
    │  path: Path
    ▼
PDFReader.read(path)
    │
    │  list[PageResult]
    ▼
Output formatter
    │
    │  formatted text
    ▼
stdout
```

The output formatter and CLI layer are consumers of `list[PageResult]`; they do not depend on which concrete reader produced it.

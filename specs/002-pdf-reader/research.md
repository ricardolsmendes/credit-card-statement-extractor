# Research: PDF Reader Module

**Phase**: 0 — Outline & Research  
**Feature**: specs/002-pdf-reader  
**Date**: 2026-04-12

---

## Decision 1: PDF Library Selection

**Decision**: Use **pdfplumber** as the initial library.

**Rationale**: Credit card statements are layout-dense documents — they typically contain tabular transaction data, multi-column sections, and headers. `pdfplumber` is built on `pdfminer.six` and provides layout-aware text extraction (`extract_text(layout=True)`) and dedicated table extraction. This makes it significantly more reliable for statement-shaped PDFs than `pypdf`, which is primarily a PDF manipulation library with basic text extraction that struggles with tables and multi-column layouts. `pdfplumber` is actively maintained (v0.11.9, Jan 2026) and MIT-licensed.

**Alternatives considered**:
- `pypdf` (v6.10.0, Apr 2026): Pure Python, great for PDF manipulation, but text extraction is layout-unaware. Rejected as default because table/column fidelity is low for statements. Remains a valid alternative reader if the user wants to compare results later.
- `pdfminer.six` directly: More control, but higher complexity for no immediate gain given `pdfplumber` wraps it cleanly.

---

## Decision 2: Swappable Reader Pattern

**Decision**: Use a **Python Protocol class** (PEP 544) to define the reader interface.

**Rationale**: A `Protocol` defines the expected interface structurally — any class implementing the required method(s) is automatically compatible without explicit inheritance. This is the idiomatic Python approach for duck-typed interfaces, keeps the abstraction lightweight, and avoids forcing a class hierarchy on alternative implementations. The interface is minimal: a callable that accepts a file path and returns structured page data.

**Alternatives considered**:
- Abstract Base Class (`abc.ABC`): More explicit, but requires inheritance — adds coupling with no benefit here given the interface is small.
- Plain function interface (callable): Simpler but harder to type-check and extend if the reader needs configuration state (e.g., password, page range).

---

## Decision 3: Reader Interface Shape

**Decision**: The reader Protocol exposes a single method: `read(path: Path) -> list[PageResult]`, where `PageResult` is a lightweight dataclass containing `page_number: int` and `text: str`.

**Rationale**: Returning structured page data (rather than a flat string) allows the CLI layer to format page separators independently of the reader — satisfying FR-004 (page boundaries) and SC-004 (output formatting change does not require touching the reader).

---

## Constitution Compliance Notes

- **Memory**: `pdfplumber` buffers the full PDF in memory. For typical statement sizes (under 50 pages), this is well within bounds. Lazy page iteration (iterating `plumber.pages` rather than loading all at once) should be used to minimise peak usage — satisfies Constitution §V.
- **Log safety**: Raw extracted text must never be passed to loggers. Only metadata (file path, page count, elapsed time) is safe to log — satisfies Constitution §Data & Security.
- **Simplicity**: The module must not add OCR, caching, or format-detection at this stage. One reader, one interface — satisfies Constitution §VI.

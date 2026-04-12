# Tasks: PDF Reader Module

**Input**: Design documents from `specs/002-pdf-reader/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Included — the project constitution (§II) mandates TDD: tests written and failing before implementation.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add `pdfplumber` dependency and create the `pdf_reader` sub-package skeleton.

- [ ] T001 Add `pdfplumber` dependency to `pyproject.toml` and run `uv sync`
- [ ] T002 Create `src/credit_card_statement_extractor/pdf_reader/__init__.py` (empty, exports to be added later)
- [ ] T003 [P] Create `tests/unit/pdf_reader/` directory with empty `__init__.py`
- [ ] T004 [P] Create `tests/integration/pdf_reader/` directory with empty `__init__.py`
- [ ] T005 [P] Add PDF test fixtures directory `tests/fixtures/pdfs/` and place a minimal single-page PDF (`single_page.pdf`) and a 2-page PDF (`multi_page.pdf`) in it — use any freely available sample PDF or generate with a script

**Checkpoint**: `uv sync` succeeds; `import pdfplumber` works; fixture PDFs are in place.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the `PDFReader` Protocol and `PageResult` dataclass — shared types that all user stories depend on.

- [ ] T006 [P] Write unit tests for `PageResult` construction and field validation in `tests/unit/pdf_reader/test_protocol.py` — must FAIL (import will fail) until T007 is complete
- [ ] T007 Create `src/credit_card_statement_extractor/pdf_reader/_protocol.py` containing the `PageResult` frozen dataclass (`page_number: int`, `text: str`) and the `PDFReader` Protocol with method `read(path: Path) -> list[PageResult]`
- [ ] T008 Update `src/credit_card_statement_extractor/pdf_reader/__init__.py` to export `PDFReader`, `PageResult`

**Checkpoint**: `uv run pytest tests/unit/pdf_reader/test_protocol.py` passes; `PageResult` and `PDFReader` are importable from the package.

---

## Phase 3: User Story 1 — Read a PDF File and Print Its Contents (Priority: P1) 🎯 MVP

**Goal**: A developer can run `python -m credit_card_statement_extractor.pdf_reader <file>` and see the extracted text of every page printed to stdout with page separators.

**Independent Test**: Run `python -m credit_card_statement_extractor.pdf_reader tests/fixtures/pdfs/single_page.pdf` — text appears on stdout with `--- Page 1 ---` header. Run with `multi_page.pdf` — both pages appear with distinct headers.

### Tests for User Story 1 ⚠️ Write FIRST — must FAIL before implementation

- [ ] T009 [P] [US1] Write unit tests for `PdfplumberReader.read()` in `tests/unit/pdf_reader/test_pdfplumber_reader.py`: single-page extraction returns one `PageResult`; multi-page returns one `PageResult` per page in order; page text is non-empty for fixture PDFs
- [ ] T009b [P] [US1] Add a timing smoke test in `tests/unit/pdf_reader/test_pdfplumber_reader.py`: extract `multi_page.pdf` fixture and assert elapsed time is under 5 seconds using `time.monotonic()` — satisfies SC-001 and Constitution §V benchmark tracking
- [ ] T010 [P] [US1] Write integration (CLI) tests in `tests/integration/pdf_reader/test_cli.py` using `subprocess`: valid single-page PDF → exit code 0 and `--- Page 1 ---` in stdout; valid multi-page PDF → exit code 0 and all page headers present

### Implementation for User Story 1

- [ ] T011 [US1] Create `src/credit_card_statement_extractor/pdf_reader/_pdfplumber_reader.py` implementing `PdfplumberReader` — satisfies the `PDFReader` Protocol; iterates `plumber.pages` lazily; returns `list[PageResult]`; raises `FileNotFoundError` for missing path, `ValueError` for unparseable PDF (depends on T007)
- [ ] T012 [US1] Create `src/credit_card_statement_extractor/pdf_reader/__main__.py` — reads `sys.argv[1]` as file path, instantiates `PdfplumberReader`, calls `read()`, and prints `--- Page N ---\n<text>` for each page to stdout; exits with code 0 on success (depends on T011)
- [ ] T013 [US1] Update `src/credit_card_statement_extractor/pdf_reader/__init__.py` to also export `PdfplumberReader`

**Checkpoint**: `uv run pytest tests/unit/pdf_reader/test_pdfplumber_reader.py tests/integration/pdf_reader/test_cli.py` passes; running the module manually prints page-separated text.

---

## Phase 4: User Story 2 — Meaningful Error Feedback on Invalid Input (Priority: P2)

**Goal**: Missing argument, missing file, and non-PDF file each produce a distinct, human-readable error message on stderr and a non-zero exit code. No raw tracebacks are shown.

**Independent Test**: Run the module with no args → exit 1, usage message on stderr. Run with a non-existent path → exit 1, "file not found" on stderr. Run with `tests/fixtures/pdfs/not_a_pdf.txt` → exit 2, "could not parse as PDF" on stderr.

### Tests for User Story 2 ⚠️ Write FIRST — must FAIL before implementation

- [ ] T014 [US2] Add a `tests/fixtures/pdfs/not_a_pdf.txt` fixture (any plain text file)
- [ ] T015 [P] [US2] Extend `tests/integration/pdf_reader/test_cli.py` with error-path cases: no argument → exit code 1 and usage message on stderr; non-existent path → exit code 1 and "not found" on stderr; non-PDF file → exit code 2 and "could not parse" on stderr; verify stdout is empty in all error cases

### Implementation for User Story 2

- [ ] T016 [US2] Update `src/credit_card_statement_extractor/pdf_reader/__main__.py` to handle missing argument (print usage to stderr, exit 1), `FileNotFoundError` (print "Error: File not found: <path>" to stderr, exit 1), and `ValueError` (print "Error: Could not parse as PDF: <path>" to stderr, exit 2); ensure no tracebacks reach stderr (depends on T012)

**Checkpoint**: `uv run pytest tests/integration/pdf_reader/test_cli.py` passes all error-path cases; running manually with bad inputs shows clean messages.

---

## Phase 5: User Story 3 — Swappable Reader Architecture (Priority: P3)

**Goal**: The reader component is isolated such that substituting the underlying library requires only adding a new file and updating one import — no changes to the CLI entry point or output formatting code.

**Independent Test**: Verify by code review that `__main__.py` imports only from `_protocol.py` and the concrete reader — not from `pdfplumber` directly. Optionally: write a `NullReader` stub that satisfies the Protocol and confirm `__main__.py` works with it by swapping the import.

### Tests for User Story 3 ⚠️ Write FIRST — must FAIL before implementation

- [ ] T017 [P] [US3] Write a structural test in `tests/unit/pdf_reader/test_protocol.py`: create a `NullReader` class inline that implements `PDFReader` Protocol; assert it passes `isinstance(NullReader(), PDFReader)` (or equivalent runtime check) without inheriting from any base class — confirms the Protocol is correctly defined for structural subtyping

### Implementation for User Story 3

- [ ] T018 [US3] Audit `src/credit_card_statement_extractor/pdf_reader/__main__.py` — confirm it references only `PDFReader`/`PageResult` types and the single concrete reader class; add an inline comment marking the one line to change to swap libraries (depends on T012)
- [ ] T019 [US3] Update module-level docstring in `src/credit_card_statement_extractor/pdf_reader/__init__.py` to document the swap pattern: "To use a different PDF library, implement the `PDFReader` Protocol and update the import in `__main__.py`"

**Checkpoint**: `uv run pytest tests/unit/pdf_reader/test_protocol.py` passes structural test; code review confirms single-point-of-change for library swap.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, linting, and verification against the quickstart.

- [ ] T020 [P] Run `uv run ruff check . && uv run ruff format --check .` — fix any violations
- [ ] T021 [P] Run full test suite `uv run pytest` — all tests must pass, no warnings
- [ ] T022 Follow `specs/002-pdf-reader/quickstart.md` end-to-end: install deps, run against a real PDF, verify output matches expected format
- [ ] T023 Verify exit code conventions match `specs/002-pdf-reader/contracts/cli-contract.md` — manually test each scenario

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **blocks all user stories**
- **User Story Phases (3, 4, 5)**: All depend on Phase 2 completion
  - US2 (Phase 4) depends on US1 (Phase 3) because error handling extends the CLI entrypoint built in US1
  - US3 (Phase 5) is a review/audit of the architecture built in Phase 2 + US1 — can begin after T011/T012 are done
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no story dependencies
- **US2 (P2)**: Starts after US1 (T012 must exist to be extended)
- **US3 (P3)**: Starts after US1 (T011, T012 must exist to audit)

### Within Each Phase

- Write tests → ensure they **FAIL** → implement → ensure they **PASS**
- Models/protocol before readers; readers before CLI entry point
- Fixtures must exist before tests that reference them

### Parallel Opportunities

- T003, T004, T005 can run in parallel (Setup)
- T006 (protocol tests) can be written while reviewing the protocol design, but must fail before T007 implementation is complete
- T009, T009b, T010 (US1 tests) can be written in parallel with each other
- T015 (US2 tests), T017 (US3 structural test) can be written in parallel once Phase 2 is done
- T020, T021 (linting + test suite) can run in parallel in Polish phase

---

## Parallel Example: User Story 1

```bash
# Write tests in parallel (different files, no shared state):
Task T009:  "Unit tests for PdfplumberReader in tests/unit/pdf_reader/test_pdfplumber_reader.py"
Task T009b: "Timing smoke test (SC-001) in tests/unit/pdf_reader/test_pdfplumber_reader.py"
Task T010:  "CLI integration tests in tests/integration/pdf_reader/test_cli.py"

# Then implement sequentially:
Task T011: "_pdfplumber_reader.py"  (depends on T007)
Task T012: "__main__.py"            (depends on T011)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational — `PageResult` + `PDFReader` Protocol
3. Complete Phase 3: User Story 1 — `PdfplumberReader` + `__main__.py`
4. **STOP and VALIDATE**: `python -m credit_card_statement_extractor.pdf_reader <sample.pdf>` prints text
5. Demo / verify before continuing

### Incremental Delivery

1. Phase 1 + 2 → protocol and types ready
2. Phase 3 (US1) → core extraction works → **MVP shippable**
3. Phase 4 (US2) → error handling → production-grade
4. Phase 5 (US3) → architecture validated → swap-ready
5. Phase 6 → polished and verified

---

## Notes

- [P] tasks touch different files and have no shared in-flight dependencies
- Constitution §II mandates TDD: all test tasks must be done and failing before their paired implementation tasks
- Never log `PageResult.text` — only metadata (file path, page count)
- Fixture PDFs must be real PDF files, not mocks — per Constitution §III
- Exit codes must exactly match `contracts/cli-contract.md`: 0 / 1 / 2

# Credit Card Statement Extractor Constitution

## Core Principles

### I. Code Quality (NON-NEGOTIABLE)
Write clean, readable, self-documenting Python. Functions do one thing. Modules have a single responsibility. Complexity must earn its place — if it can be simpler, it must be. Ruff enforces style; violations block merges. Dead code, commented-out blocks, and TODO-as-code are not allowed to accumulate.

### II. Test-First (NON-NEGOTIABLE)
TDD mandatory: tests written and approved before implementation begins. Red → Green → Refactor cycle strictly enforced. A feature is not done until its tests pass. No production code exists without a corresponding test. Coverage must not regress.

### III. Testing Standards
- **Unit tests**: Every parsing function, data transformation, and business logic path covered
- **Integration tests**: Full pipeline from raw statement input to structured output
- **Edge cases mandatory**: Malformed input, missing fields, unsupported formats, encoding issues
- **Fixtures over mocks**: Use real sample statement files as test fixtures; mock only external I/O boundaries (file system, network)
- Tests live alongside the code they test; test names describe behavior, not implementation

### IV. User Experience Consistency
- CLI interface is the primary contract: stdin/args → stdout, errors → stderr
- Output is deterministic and machine-readable by default (JSON); human-readable format available via flag
- Error messages are actionable — they tell the user what went wrong and how to fix it
- Exit codes are meaningful and documented: 0 = success, 1 = user error, 2 = parse failure, 3 = internal error
- No silent failures; every error path produces output

### V. Performance Requirements
- Single statement extraction completes in under 2 seconds on standard hardware
- Memory usage scales linearly with input size; no unbounded accumulation
- Parsing is lazy where possible — do not load the entire file into memory unless required
- Benchmarks are tracked; regressions require justification before merge

### VI. Simplicity
Start with the simplest thing that works. YAGNI: no speculative features, no premature abstractions. A new abstraction requires two concrete use cases to justify it. Dependencies are liabilities — add only what is essential.

## Data & Security Constraints

- Statement files may contain sensitive financial data; never log raw statement content
- No data is transmitted externally; this tool operates entirely offline
- Parsed output must not include credentials, account numbers in full (mask to last 4 digits), or security codes
- Input validation is strict: reject unrecognized formats explicitly rather than partially parsing them

## Development Workflow

- All work begins with a spec; no implementation without an approved spec
- Branches are short-lived; features merge within the sprint they are started
- PRs require passing tests, no linting violations, and at least one review
- Constitution compliance is verified at every PR review
- Breaking changes to the CLI contract require a major version bump and migration notes

## Governance

This constitution supersedes all other practices in this repository. Amendments require a documented rationale, approval, and a migration plan for any affected code. All PRs must verify compliance with these principles. The constitution is a living document — revisit it when the project outgrows it, not before.

**Version**: 1.0.0 | **Ratified**: 2026-04-10 | **Last Amended**: 2026-04-10

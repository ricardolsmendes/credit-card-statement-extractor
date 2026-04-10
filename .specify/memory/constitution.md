<!--
SYNC IMPACT REPORT
==================
Version change: (unversioned template) → 1.0.0
Added sections: Core Principles (I–IV), Quality Standards, Development Workflow, Governance
Removed sections: N/A (initial authoring from template)
Modified principles: N/A (initial authoring)
Templates requiring updates:
  ✅ plan-template.md — Constitution Check gates updated to reference these four principles
  ✅ spec-template.md — Success Criteria and Functional Requirements align with principles
  ✅ tasks-template.md — Task phases reflect test-first and performance-gate requirements
Deferred TODOs: None
-->

# Credit Card Statement Extractor Constitution

## Core Principles

### I. Code Quality (NON-NEGOTIABLE)

Every change to this codebase MUST meet the following quality bar before merge:

- Code MUST be readable without inline comments; if a comment is needed, simplify the logic first.
- Functions and methods MUST have a single, clear responsibility; any routine that requires
  "and" in its description MUST be split.
- Magic numbers, hardcoded paths, and environment-specific values MUST be extracted into
  named constants or configuration.
- Dead code, commented-out blocks, and unused imports MUST be removed before merge.
- Linting and static analysis checks MUST pass with zero warnings on every commit.

**Rationale**: Statement extraction operates on financial data. Ambiguous or brittle code
increases the risk of silent mis-extractions that are difficult to audit after the fact.

### II. Test-First Development (NON-NEGOTIABLE)

All new functionality MUST follow a strict Red-Green-Refactor cycle:

1. Write a failing test that precisely describes the expected behavior.
2. Obtain approval (or self-review confirmation) that the test is correct.
3. Implement the minimum code required to make the test pass.
4. Refactor while keeping tests green.

Additional rules:
- Unit tests MUST cover all extraction logic (parsing, field mapping, validation).
- Integration tests MUST cover end-to-end statement ingestion with real fixture files.
- Tests MUST be deterministic; any test that relies on network calls or wall-clock time
  MUST use fixtures or dependency injection.
- A PR MUST NOT lower the project's overall test coverage percentage.

**Rationale**: Financial extraction errors are silent and consequential. Tests are the primary
safety net ensuring accuracy across statement formats and edge cases.

### III. User Experience Consistency

Every user-facing output or interface MUST adhere to these standards:

- Output field names and data formats MUST be consistent across all statement formats
  (e.g., date always `YYYY-MM-DD`, amount always a decimal string with two places).
- Error messages MUST be actionable: they MUST state what went wrong AND what the user
  can do to resolve it.
- CLI flags and configuration keys MUST follow a single naming convention
  (kebab-case for CLI, snake_case for config files) and MUST NOT be changed without a
  deprecation notice in the changelog.
- Where multiple statement formats are supported, the output schema MUST be identical;
  format-specific quirks MUST be normalized before output.

**Rationale**: Users build downstream workflows (budgeting, reporting) on top of this
tool's output. Inconsistent field names or formats silently corrupt those workflows.

### IV. Performance Requirements

The extractor MUST meet these benchmarks under standard test conditions
(commodity laptop, single core, local file I/O):

- A single statement file (≤ 5 MB) MUST be fully processed in under **5 seconds**.
- Batch processing of 50 statement files MUST complete in under **120 seconds**.
- Memory usage MUST NOT exceed **256 MB** during any single-file extraction.
- Performance regression tests MUST be run and MUST pass on every PR that touches
  extraction or parsing code.

**Rationale**: Extraction is often run as part of automated pipelines. Exceeding these
thresholds blocks real-time use cases and increases cloud compute costs.

## Quality Standards

- All merged code MUST pass CI (lint, tests, type checks) without manual overrides.
- Type annotations MUST be present on all public functions and class signatures.
- New statement format support MUST include at least one fixture file and a corresponding
  test suite before the format is considered supported.
- Dependency upgrades MUST be validated by running the full test suite; breaking changes
  in dependencies MUST be addressed before merging the upgrade.

## Development Workflow

- Feature work MUST be done on a branch (naming: `###-short-description`).
- Every branch MUST have an associated spec in `specs/###-feature-name/spec.md` before
  implementation begins.
- The Constitution Check in `plan.md` MUST be completed and passing before Phase 0
  research begins.
- PRs MUST reference their spec and include a brief test plan in the description.
- Commits SHOULD be atomic and describe *why* the change was made, not just *what*.

## Governance

- This constitution supersedes all other project practices and informal conventions.
- Amendments require: (1) a written rationale, (2) an updated version number per
  semantic versioning rules below, and (3) updates to all dependent templates.
- **Versioning policy**:
  - MAJOR — backward-incompatible principle removals or redefinitions.
  - MINOR — new principle or section added, or materially expanded guidance.
  - PATCH — clarifications, wording fixes, non-semantic refinements.
- All PRs and code reviews MUST verify compliance with this constitution.
- Complexity that violates a principle MUST be justified in the plan's
  Complexity Tracking table and approved before implementation.

**Version**: 1.0.0 | **Ratified**: 2026-04-09 | **Last Amended**: 2026-04-09
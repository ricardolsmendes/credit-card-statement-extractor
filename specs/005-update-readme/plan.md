# Implementation Plan: Update README with Capabilities and Developer Guide

**Branch**: `005-update-readme-capabilities` | **Date**: 2026-04-14 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/005-update-readme/spec.md`

---

## Summary

Rewrite `README.md` at the repository root to replace the current one-line description with a complete user-facing document covering: project overview, installation, CLI usage with examples, expected output, and a Developer's Guide section that names Claude Code and GitHub Speckit as the primary development tools.

---

## Technical Context

**Language/Version**: Markdown (CommonMark / GitHub Flavored Markdown)  
**Primary Dependencies**: None — pure documentation edit  
**Storage**: Single file: `README.md` at repository root  
**Testing**: Manual review — render on GitHub and verify all FRs are satisfied  
**Target Platform**: GitHub repository page (primary); terminal plain-text (secondary)  
**Project Type**: Documentation update  
**Performance Goals**: A new user can go from reading to running in under 5 minutes (SC-001)  
**Constraints**: Must render correctly on GitHub; no broken links; plain-text readable  
**Scale/Scope**: Single file; no dependencies; no code changes

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| §I Code Quality | ✅ | No code changes; documentation only |
| §II Test-First | ✅ | Manual acceptance criteria defined in spec (FR-001–FR-010); no automated tests needed for a Markdown file |
| §III Testing Standards | ✅ | Verification: read README against each FR before marking complete |
| §IV UX Consistency | ✅ | README content is additive; no CLI behaviour changes |
| §V Performance | ✅ | No performance impact |
| §VI Simplicity | ✅ | Single file edit; no abstractions introduced |
| Data & Security | ✅ | No sensitive data; no external transmission |

No violations. No Complexity Tracking entry required.

---

## Phase 0 Output: Research

No technical unknowns. All decisions are deterministic from the existing codebase state and the spec:

### Decision 1: README structure

- **Decision**: Standard open-source README structure — Overview → Installation → Usage → Developer's Guide
- **Rationale**: Matches GitHub conventions; satisfies FR-001 through FR-010 in natural reading order
- **Alternatives considered**: Single-section dump (rejected — poor scannability); separate CONTRIBUTING.md for dev guide (rejected — overkill for a pet project; spec says a section in README)

### Decision 2: Installation method

- **Decision**: `uv sync` as primary; brief `pip install -e .` as fallback note
- **Rationale**: `uv` is the project's declared dependency manager (CLAUDE.md); `pip` fallback covers users without `uv`
- **Alternatives considered**: `pip install` only (rejected — misrepresents the actual dev workflow)

### Decision 3: Claude Code and Speckit links

- **Decision**: Link Claude Code to `https://claude.ai/code` and GitHub Speckit to `https://github.com/github/spec-kit` (same links as current README)
- **Rationale**: Official pages; already used in the existing one-line README; stable URLs
- **Alternatives considered**: No links (rejected — FR-007 implies enough context for a reader to find the tools)

### Decision 4: Output examples

- **Decision**: Show both table output (default) and CSV file content as examples
- **Rationale**: Demonstrates the two most common use cases; stays under quickstart length; matches `specs/004-export-csv-xlsx/quickstart.md` content
- **Alternatives considered**: XLSX example (impractical in Markdown — binary format); all 3 formats (too long)

---

## Phase 1 Output: Design

### Source Code Changes

```text
README.md    ← UPDATED: full rewrite with overview, installation, usage, developer guide
```

No other files changed. No new directories. No new source modules.

### README Structure

```
# Credit Card Statement Extractor

## Overview
## Installation
## Usage
### Basic table output
### Export to CSV
### Export to XLSX
### All options
## Developer's Guide
### Development tools
### Development commands
```

### Contract: README Content Requirements

Each section maps directly to a Functional Requirement:

| Section | FR(s) | Content |
|---------|-------|---------|
| Overview | FR-001, FR-010 | 2–3 sentence description; incorporates existing description |
| Installation | FR-002 | `uv sync` steps; pip fallback |
| Usage — table | FR-003, FR-004 | CLI invocation + sample tabular output |
| Usage — CSV | FR-003, FR-004, FR-005 | `--output-format csv` + sample CSV content |
| Usage — XLSX | FR-003, FR-005 | `--output-format xlsx` brief note |
| All options | FR-005 | Table of arguments: `file_path`, `--lang`, `--output-format` |
| Developer's Guide | FR-006, FR-007, FR-008 | Claude Code + Speckit descriptions; test/lint commands |

### Quickstart

No separate `quickstart.md` needed — `specs/004-export-csv-xlsx/quickstart.md` already documents all CLI scenarios. The README summarises the key paths.

---

## Project Structure

### Documentation (this feature)

```text
specs/005-update-readme/
├── plan.md              ← this file
├── research.md          ← (inline above — no separate file needed)
└── tasks.md             (generated by /speckit.tasks)
```

### Source Code

```text
README.md    ← only file changed
```

**Structure Decision**: Single-file documentation update. No source code, no tests, no new modules.

---

## Key Implementation Notes

### Preserving existing content (FR-010)

The current README contains:
> "A CLI application to extract structured data from credit card statements and export it in CSV or XLSX. This is a pet project that I'm developing in order to learn how to use Claude Code and GitHub Spec Kit."

This becomes the seed for the Overview section — expanded, not replaced.

### CLI arguments table (FR-005)

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `file_path` | positional | — | Path to the PDF credit card statement |
| `--lang` | option | `en` | Output language: `en` or `pt-BR` |
| `--output-format` | option | — | Export format: `csv` or `xlsx` (omit to print table) |

### Developer's Guide content (FR-007)

- **Claude Code**: AI-powered CLI that writes, edits, and runs code in response to natural language instructions. Used for all implementation tasks in this project.
- **GitHub Speckit**: Specification-driven development workflow tool. Used to write specs, generate implementation plans, and drive TDD task breakdowns before any code is written.

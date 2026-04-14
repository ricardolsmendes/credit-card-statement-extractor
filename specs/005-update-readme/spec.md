# Feature Specification: Update README with Capabilities and Developer Guide

**Feature Branch**: `005-update-readme-capabilities`  
**Created**: 2026-04-14  
**Status**: Draft  
**Input**: User description: "Once the application MVP is in good shape, the `README.md` file at the repository's root folder must be updated to briefly describe its capabilities and usage instructions. A `Developer's guide` section should also be included, highlighting the project uses Claude Code and GitHub Speckit as the main development tools."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — New User Reads the README to Understand and Use the Tool (Priority: P1)

A developer or technical user discovers the repository (e.g., on GitHub) and reads the README to understand what the tool does, how to install it, and how to run it. They should be able to follow the README alone and successfully extract transactions from a PDF statement and export them.

**Why this priority**: This is the primary purpose of a README — to get a new user from zero to working in the shortest time. If this story fails, the project is effectively undiscoverable.

**Independent Test**: Open the README in isolation (without access to any other docs) and verify that a technically proficient user can install the package, run the CLI against a PDF, and understand the output format — all from the README content alone.

**Acceptance Scenarios**:

1. **Given** a new user has cloned the repository, **When** they read the README, **Then** they understand the tool's purpose in one paragraph or less.
2. **Given** a new user reads the README, **When** they follow the installation instructions, **Then** they can install the tool and its dependencies without consulting any other document.
3. **Given** a user has the tool installed, **When** they follow the usage examples in the README, **Then** they can successfully run the CLI and produce CSV or XLSX output from a PDF statement.
4. **Given** a user reads the README, **When** they look for output format information, **Then** they find at least one example showing what the extracted output looks like.

---

### User Story 2 — Contributor Reads the Developer's Guide to Understand the Development Workflow (Priority: P2)

A developer who wants to contribute to or study the project reads the Developer's Guide section to understand the development tooling, the workflow used to build the project, and how Claude Code and GitHub Speckit fit into that workflow.

**Why this priority**: The project's secondary stated goal is to demonstrate and document the use of Claude Code and GitHub Speckit as development tools. This section fulfills that goal and is required by the feature description.

**Independent Test**: A developer new to this project can read the Developer's Guide section and understand: what tools are used, why, and how to run the development commands (tests, linting) without consulting any other document.

**Acceptance Scenarios**:

1. **Given** a developer reads the Developer's Guide section, **When** they finish reading, **Then** they understand that Claude Code and GitHub Speckit are the primary development tools and know what each one does.
2. **Given** a developer reads the Developer's Guide section, **When** they look for development commands, **Then** they find commands for running tests and linting.
3. **Given** a developer reads the README, **When** they scan the section headings, **Then** the Developer's Guide section is clearly identified and easy to locate.

---

### Edge Cases

- What if a user reads the README on a platform that does not render Markdown (e.g., plain-text terminal)? The README must be readable as plain text — no ASCII art or complex tables that degrade badly.
- What if the tool's capabilities expand beyond what the README describes? The README should describe current MVP capabilities only, not speculative future features.
- What if the existing one-line README content conflicts with the new expanded content? The existing content should be incorporated or superseded — no duplication.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The README MUST include a brief description (one to three sentences) of what the tool does and who it is for.
- **FR-002**: The README MUST include installation instructions sufficient for a new user to set up the tool from scratch.
- **FR-003**: The README MUST include at least one usage example showing how to run the CLI against a PDF statement.
- **FR-004**: The README MUST show at least one example of expected output (e.g., sample CSV content or CLI table output).
- **FR-005**: The README MUST document the supported CLI arguments and flags (`--lang`, `--output-format`).
- **FR-006**: The README MUST include a Developer's Guide section.
- **FR-007**: The Developer's Guide MUST mention Claude Code and GitHub Speckit by name and briefly describe their role in the project's development workflow.
- **FR-008**: The Developer's Guide MUST include commands for running the test suite and linter.
- **FR-009**: The README MUST be written in Markdown and render correctly on GitHub.
- **FR-010**: The existing project description in the current README MUST be preserved or naturally incorporated into the new content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can go from reading the README to running their first successful CLI command in under 5 minutes.
- **SC-002**: All CLI flags and their allowed values are documented — zero undocumented flags after the update.
- **SC-003**: The Developer's Guide section is present and names both Claude Code and GitHub Speckit with a brief description of each tool's role.
- **SC-004**: The README renders without errors on GitHub (no broken links, no malformed Markdown, no raw HTML required).

## Assumptions

- The README targets technically proficient users (developers, data analysts) comfortable with a terminal — no GUI or wizard walkthrough is needed.
- Installation assumes `uv` is the primary package manager; a `pip install` fallback note is a nice-to-have but not required.
- The README describes current MVP capabilities only: PDF parsing, table output, CSV export, and XLSX export.
- The existing one-sentence description in the current README is the seed for the new description — it should be expanded, not discarded.
- Links to external tools (Claude Code, GitHub Speckit) should point to official pages.
- The README does not need to cover every error scenario — the tool's stderr output handles errors; the README covers the happy path only.

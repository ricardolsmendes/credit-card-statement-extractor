# Feature Specification: Python Project Setup

**Feature Branch**: `001-python-project-setup`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: User description: "To start the project, let's set up some configurations for Python, as follows: 1. The main application code must reside within the `src` folder. 2. Tests must reside within the `tests` folder. 3. `pyproject.toml` is the preferred way to store project configurations."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Runs Application Code (Priority: P1)

A developer clones the repository and immediately knows where to find and place application source code. All application logic lives under `src/`, making the structure self-evident and consistent with Python packaging conventions.

**Why this priority**: The source layout is foundational — every other workflow (testing, packaging, running) depends on where application code lives. Without this, developers cannot contribute or run the project.

**Independent Test**: Can be fully tested by verifying a developer can navigate to `src/` and locate (or place) Python modules, and that running the application entry point from the project root works correctly.

**Acceptance Scenarios**:

1. **Given** a freshly cloned repository, **When** a developer looks for application source code, **Then** they find it under the `src/` directory
2. **Given** the `src/` directory exists, **When** a new module is added to `src/`, **Then** it is recognized as part of the application without additional configuration

---

### User Story 2 - Developer Runs Tests (Priority: P2)

A developer wants to run the project's test suite. All tests reside under `tests/`, keeping them separate from application code and discoverable by standard test tooling without additional path configuration.

**Why this priority**: A working test setup is the second most critical element — it validates that the source layout is correct and enables quality assurance from day one.

**Independent Test**: Can be fully tested by placing a sample test file in `tests/` and confirming it is discovered and executed by the test runner without additional configuration.

**Acceptance Scenarios**:

1. **Given** the repository is set up, **When** a developer invokes the test runner from the project root, **Then** all tests under `tests/` are discovered and executed
2. **Given** a new test file is added to `tests/`, **When** the test runner is invoked, **Then** the new test is automatically included without modifying any configuration

---

### User Story 3 - Developer Inspects or Updates Project Configuration (Priority: P3)

A developer needs to check or modify project metadata (name, version, dependencies, tool settings). All project configuration is consolidated in a single `pyproject.toml` file at the project root, eliminating the need to hunt across multiple config files.

**Why this priority**: Centralised configuration reduces friction for contributors and tooling; it comes after the structural setup is in place.

**Independent Test**: Can be fully tested by verifying `pyproject.toml` exists at the project root, contains the mandatory project metadata, and that adding a new dependency or tool setting to it is immediately effective.

**Acceptance Scenarios**:

1. **Given** the repository is set up, **When** a developer opens `pyproject.toml`, **Then** they find all project metadata and tool configuration in that single file
2. **Given** a developer adds a new dependency to `pyproject.toml`, **When** dependencies are installed, **Then** the new dependency is available to the application and tests
3. **Given** `pyproject.toml` exists, **When** any legacy configuration files (e.g., `setup.py`, `setup.cfg`, `tox.ini`) are present, **Then** `pyproject.toml` is treated as the authoritative source and legacy files are not required

---

### Edge Cases

- What happens when a developer accidentally places application code outside `src/`? The project structure and documentation should make the correct location unambiguous.
- How does the test runner handle test files placed outside `tests/`? By convention, only files inside `tests/` are discovered; files elsewhere are not treated as tests.
- What happens if `pyproject.toml` is missing? The project cannot be installed or configured; its presence is a hard requirement.
- How are configuration values in `pyproject.toml` validated? Malformed or missing mandatory fields (name, version) should produce a clear error when the project is installed or built.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST have a `src/` directory at the root that contains all application source code
- **FR-002**: The project MUST have a `tests/` directory at the root that contains all test code
- **FR-003**: Application code and test code MUST be kept strictly separate — no test files inside `src/`, no application modules inside `tests/`
- **FR-004**: The project MUST have a `pyproject.toml` file at the root that serves as the single source of project configuration
- **FR-005**: `pyproject.toml` MUST include, at minimum, the project name, version, and any declared dependencies
- **FR-006**: The test runner MUST discover and execute all tests under `tests/` without requiring manual path specification
- **FR-007**: The source layout MUST allow the application package(s) under `src/` to be importable by the test suite without path manipulation by the developer
- **FR-008**: All tool-specific settings (linter, formatter, test runner, etc.) MUST be configured inside `pyproject.toml` rather than in separate tool configuration files

### Key Entities

- **`src/` directory**: The root of all application source code; contains one or more Python packages or modules that make up the project
- **`tests/` directory**: The root of all test code; mirrors or complements the structure of `src/` as needed
- **`pyproject.toml`**: The single project configuration file; declares project metadata, dependencies, and tool settings

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can clone the repository and locate all application source code in `src/` within 30 seconds, with no documentation required beyond the directory name
- **SC-002**: A developer can run the full test suite from the project root with a single command and zero additional path or environment setup
- **SC-003**: 100% of project configuration (metadata, dependencies, tool settings) is discoverable in `pyproject.toml` — no configuration is split across other files
- **SC-004**: New contributors can add application code to `src/` and tests to `tests/` and have both immediately recognised by the project's tooling without editing any configuration file

## Assumptions

- The project targets Python 3 (version unspecified; a reasonable modern default will be chosen during implementation)
- The `src` layout (placing packages inside a `src/` subdirectory rather than at the project root) is the intended convention, consistent with modern Python packaging best practices
- No existing application code or test files need to be migrated; this is a greenfield setup
- The choice of test runner, linter, and formatter is deferred to the implementation phase; this spec only requires they be configurable via `pyproject.toml`
- A single `pyproject.toml` at the project root is sufficient; monorepo or multi-package layouts are out of scope
- Legacy configuration files (`setup.py`, `setup.cfg`, `requirements.txt`, etc.) will not be created as part of this setup

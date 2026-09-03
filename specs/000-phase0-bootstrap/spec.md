# Feature Specification: Phase 0 Repository Bootstrap

**Feature Branch**: `000-phase0-bootstrap`

**Created**: 2026-09-04

**Status**: Approved

**Input**: Establish a thin, contract-first, test-first full-stack foundation without Phase 1 business behavior.

## User Scenarios & Testing

### User Story 1 - Run a key-free development skeleton (Priority: P1)

As a developer, I can bootstrap and run the API and web shell using mock providers so third-party credentials or outages do not block work.

**Why this priority**: A reliable demo and shared development path are the immediate foundation for every later feature.

**Independent Test**: Start the API with default configuration, request health/provider status, and verify the web shell can request the API health contract without external keys.

**Acceptance Scenarios**:

1. **Given** no provider environment variables or API keys, **When** the API starts, **Then** it uses mock LLM and digital-human adapters and reports healthy.
2. **Given** the API is running, **When** the health endpoint is requested, **Then** it returns a response matching the published OpenAPI contract.
3. **Given** the API base URL is configured for the web app, **When** the web shell loads, **Then** it renders API health through generated contract types.

### User Story 2 - Add providers without changing the core (Priority: P2)

As an integration developer, I can implement a new LLM or digital-human adapter and select it through configuration without modifying domain, application contracts, existing use cases, or the public HTTP contract.

**Why this priority**: Real provider work will arrive next and needs a safe extension seam now.

**Independent Test**: Run the same port contract suite against each registered implementation and verify bootstrap selects configured providers.

**Acceptance Scenarios**:

1. **Given** two implementations of a port, **When** the shared contract suite runs, **Then** both exhibit the same application-visible behavior.
2. **Given** a supported provider name, **When** settings are composed, **Then** bootstrap injects the matching adapter through the application port.
3. **Given** an unsupported provider name, **When** the API is composed, **Then** startup fails with a clear configuration error rather than silently selecting a provider.

### User Story 3 - Detect architecture and contract drift (Priority: P3)

As a maintainer or coding agent, I can run one deterministic cross-platform quality gate that catches dependency violations, test failures, type/lint issues, and stale generated API artifacts.

**Why this priority**: Executable governance makes the foundation difficult to erode during fast follow-on work.

**Independent Test**: Run the Python task runner's `check` command and verify every backend, frontend, architecture, test, and generation-drift stage passes without modifying files.

**Acceptance Scenarios**:

1. **Given** a forbidden core import, **When** `architecture-check` runs, **Then** it fails.
2. **Given** a changed backend API schema without regenerated artifacts, **When** `check` runs, **Then** the drift stage fails without changing the working tree.
3. **Given** a clean checkout on Windows without Make, **When** `uv run python scripts/dev.py check` runs, **Then** it performs the same checks as `make check`.

### Edge Cases

- Provider names are normalized only as explicitly documented; unknown values fail clearly.
- Generated artifacts are compared byte-for-byte from deterministic generation.
- The quality gate reports a missing `pnpm`, incompatible Python, or missing installed dependencies as an actionable prerequisite error.
- Mock providers return structural, non-business placeholder results and perform no network I/O.

## Requirements

### Functional Requirements

- **FR-001**: The repository MUST contain separate FastAPI and Next.js applications with a shared cross-platform task runner.
- **FR-002**: Application-owned asynchronous `LLMPort` and `DigitalHumanPort` contracts MUST exist.
- **FR-003**: Deterministic mock adapters MUST implement both ports without network calls or credentials.
- **FR-004**: Bootstrap MUST select mock adapters by default and MUST select registered adapters from environment configuration.
- **FR-005**: The API MUST expose health and provider-status responses only; no Phase 1 product or shopping behavior may be added.
- **FR-006**: Import rules MUST prevent domain from importing outer layers and application from importing infrastructure, presentation, or bootstrap.
- **FR-007**: Tests MUST be organized as unit, contract, integration, and acceptance suites.
- **FR-008**: FastAPI's OpenAPI schema MUST be reproducibly written to a committed artifact.
- **FR-009**: TypeScript API contracts MUST be generated from OpenAPI under `apps/web/src/api/generated/` and include a manual-edit warning.
- **FR-010**: A thin Makefile MUST expose the required aliases while `scripts/dev.py` remains their source of truth.
- **FR-011**: `check` MUST be deterministic, non-mutating, and cover formatting, lint, static types, architecture, all backend test categories, frontend lint/typecheck, and generated drift.
- **FR-012**: CI MUST install pinned dependencies and run the Python quality gate; it MUST NOT deploy.
- **FR-013**: Agent and architecture documentation MUST encode the project constitution and placement rules concisely.

## Success Criteria

### Measurable Outcomes

- **SC-001**: API and web development servers start with mock providers and no third-party credentials.
- **SC-002**: All four test categories pass and the health endpoint returns HTTP 200.
- **SC-003**: A deliberate forbidden import causes `architecture-check` to exit non-zero.
- **SC-004**: OpenAPI and TypeScript generation are reproducible, and stale committed output causes `check` to exit non-zero.
- **SC-005**: `make check` and `uv run python scripts/dev.py check` invoke the same implementation and complete successfully on the supported toolchain.
- **SC-006**: A repository search finds none of the forbidden Phase 1 business concepts or infrastructure stacks.

## Assumptions

- Python 3.12+ and current LTS-compatible Node/pnpm are available in development and CI.
- Phase 0 needs no database, queue, cache, container, real provider SDK, or browser E2E framework.
- A minimal provider-status use case is infrastructure proof, not product behavior.
- The OpenAPI document and generated TypeScript output are committed for review and drift detection.

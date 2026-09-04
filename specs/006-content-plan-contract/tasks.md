# Tasks: Content Plan Contract

**Phase**: GREEN authorized after approved SPEC + RED; stop for review, no commit.
**Inputs**: [spec.md](spec.md), [plan.md](plan.md), approved RED tests, and the user's
GREEN instructions. Their historical RED-only stop points are superseded for
Domain/Application/mock implementation only. Frozen business contracts unchanged.
**Worktree**: `/private/tmp/liuliangchuhai-issue6-green`, branch
`feat/6-content-plan-contract`, base `182d3a90f13753b1540918b740de890cd1a1a887`.
Only the seven approved #6 documents/tests were copied from the original checkout;
no #3 RED files or shared-fixture changes were copied. Original files retained.

## Completed SPEC and RED

- [x] T001 Read governance, active/merged specs and existing core contracts.
- [x] T002 Freeze US1/US2 in specs/006-content-plan-contract/spec.md.
- [x] T003 Record placement/tests in specs/006-content-plan-contract/plan.md.
- [x] T004 [US1] Add apps/api/tests/unit/test_content_plan.py.
- [x] T005 [US1] Add apps/api/tests/contract/test_content_planner_port.py.
- [x] T006 [US1] Add apps/api/tests/unit/test_create_content_plan.py.
- [x] T007 [US2] Add apps/api/tests/contract/test_mock_content_planner.py.
- [x] T008 Review validation/identity/offline expectations and verify RED below.

## GREEN and review

- [ ] T009 Shared governance reconciliation in AGENTS.md/constitution is explicitly deferred.
- [x] T010 [US1] Implement apps/api/src/liuliangchuhai/domain/content_plan.py.
- [x] T011 [US1] Implement apps/api/src/liuliangchuhai/application/ports/content_planner.py.
- [x] T012 [US1] Implement apps/api/src/liuliangchuhai/application/use_cases/create_content_plan.py.
- [x] T013 [US2] Implement apps/api/src/liuliangchuhai/infrastructure/content/mock.py and __init__.py.
- [ ] T014 Bootstrap wiring is explicitly deferred; not required for #6 acceptance.
- [x] T015 Review #6 implementation for simplification; no further refactor needed.
- [x] T016 Run make architecture-check without weakening existing gates.
- [x] T017 Run make check and verify tracked/generated files remain unchanged.
- [ ] T018 Rebase latest main later if required for downstream wiring/governance.
- [ ] T019 Future PR verification after user review; no PR creation authorized.

US1 Domain -> Port -> UseCase -> US2 Mock -> focused suite -> architecture ->
quality gate -> stop for review. Deferred tasks do not block this scoped GREEN.

## Approved RED evidence (original checkout)

```sh
UV_CACHE_DIR=/tmp/issue6-uv-cache uv run --project apps/api --no-sync pytest apps/api/tests/unit/test_content_plan.py apps/api/tests/contract/test_content_planner_port.py apps/api/tests/unit/test_create_content_plan.py apps/api/tests/contract/test_mock_content_planner.py -q --continue-on-collection-errors
```

Exit 1: **4 errors in 0.02s**; missing Domain, Port, UseCase, and mock package.
Final RED review added the mock-only random/clock import guard; tests had no #3
contract dependency. Existing committed tests: **141 passed in 0.21s**.
Original mixed worktree full suite: **26 failed, 143 passed, 6 errors in 0.93s**;
26 failures/two collection errors were pre-existing #3 RED, four errors were #6.
Original make check passed format/lint/type/architecture, then stopped at RED.

## GREEN evidence (independent worktree)

- Approved tests copied byte-for-byte; no test edits, skips, xfails or stubs.
- Incremental runs used `PYTHONPATH=apps/api/src` with the original checkout's
  installed Python interpreter while the isolated environment was being prepared:
  Domain **70 passed**, Port **2 passed**, UseCase **12 passed**, Mock **4 passed**.
- Combined focused suite: **88 passed in 0.04s**, without collection-error bypass.
- Isolated environment installed from unchanged uv.lock; frontend dependencies
  copied with filesystem cloning, without sharing a mutable node_modules tree.
- Focused GREEN command (exit 0, **88 passed in 0.04s**):
  `UV_CACHE_DIR=/tmp/issue6-uv-cache uv run --project apps/api --no-sync pytest apps/api/tests/unit/test_content_plan.py apps/api/tests/contract/test_content_planner_port.py apps/api/tests/unit/test_create_content_plan.py apps/api/tests/contract/test_mock_content_planner.py -q`
- `UV_CACHE_DIR=/tmp/issue6-uv-cache make architecture-check`: exit 0,
  **4 kept, 0 broken**; core import policy passed.
- `UV_CACHE_DIR=/tmp/issue6-uv-cache make check`: exit 0, **All checks passed**.
  Format/lint/mypy passed; unit **201**, contract **22**, integration **4**,
  acceptance **2** passed (**229 total**). Frontend lint/typecheck/build and
  generated-contract drift check passed; candidates were generated only in temp.
- `git diff --check` passed; tracked baseline hashes are unchanged. All approved
  #6 tests/spec/plan are byte-identical to their originals. No #3 work included.
- `git diff --stat`/`git diff` are empty because all 12 #6 files are untracked;
  reviewed new production files with git diff --no-index against /dev/null.
  Five production files added (101 lines); no bootstrap or existing contract edits.
- No commit, push, PR, provider integration, dependencies, or unrelated refactor.

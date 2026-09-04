# Tasks: Product Analysis Frontend

**Branch**: `feat/4-product-analysis-frontend` | **Scope**: Approved SPEC + RED -> GREEN.
Stop for review before commit, push or PR.

## Completed SPEC + RED

- [x] T001 Read live Issue #4, root/web AGENTS, constitution, #3/#17 artifacts,
  existing generated types, health helper, app files and installed Next.js guides.
- [x] T002 Fetch and track the already-existing remote branch; verify it matches
  origin/main and contains merged #17. Run the frontend baseline before RED.
- [x] T003 Write compact spec/plan/tasks and scope the 1.5.0 amendment; update
  active-spec guidance without changing Core Principles or backend contracts.
- [x] T004 Add only selection.contract.ts, locking two future API function
  signatures to generated paths; run focused frontend typecheck and record RED.
- [x] T005 Review status/diff/check/stat and scope; stop for review before GREEN.

## Authorized GREEN

- [x] T006 Implement api/selection.ts with generated aliases, normalization and
  stable error mapping; make the existing type probe pass without weakening it.
- [x] T007 Implement only /analysis and the workbench/CSS: six UI states, empty
  catalog, labeled inputs, submit guard and the complete heuristic analysis report.
- [x] T008 If practical, perform the light manual smoke allowed by the GREEN
  instruction; record observed behavior/screenshots and limits without new tooling.
- [x] T009 Run frontend lint/typecheck/build and make check; review unchanged
  backend/generated/dependency/root-page scope and stop before commit/push/PR.

## Baseline evidence

At `4ea67a94dd4bc549a7ad9201e2dc9bb13c762434`, the branch matched origin/main and
contained #17's implementation and guidance commits. Worktree was clean.

Before any RED changes, `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache make check`
exited **0**, all checks passed. This repository-equivalent baseline invoked
`pnpm lint`, `pnpm typecheck`, `pnpm build` in apps/web: all **exit 0**. Next.js build
completed; existing `/` and `/_not-found` routes remained. Backend tests **318 passed**
(242 unit, 39 contract, 35 integration, 2 acceptance), type/lint/architecture checks
and generated drift passed. Generation for drift checking wrote only temporary
candidates; tracked OpenAPI and TypeScript were not regenerated or modified.

## RED and review evidence

Executed from repository root:

```sh
pnpm --dir apps/web typecheck
```

Exit **2**, exactly **one TypeScript diagnostic**:

```text
src/features/selection/selection.contract.ts(18,70): error TS2307: Cannot find module '@/api/selection' or its corresponding type declarations.
```

Only the planned Issue #4 API implementation is missing. Generated types resolve;
no additional type failures, stubs, suppressions, runtime code, fetch calls or test
framework were introduced. `pnpm --dir apps/web lint` after RED exits **0**.
At the RED checkpoint, typecheck/build were intentionally not GREEN; UI behavior was deferred
to T008, and the fully passing gate above applies to the pre-edit baseline only.

Reviewed `git status --short`, `git diff --check`, `git diff --stat`, `git diff`
and the new files. Tracked changes are only constitution (one scoped paragraph,
1.4.0 -> 1.5.0) and AGENTS active-spec/phase guidance. Core Principles and remaining
architecture guidance are unchanged. New files are these three documents and the
18-line type-only probe. The ignored local `.specify/feature.json` pointer also
tracks this active spec. No apps/api, generated schema, root app files, #5 UI,
existing tests, dependency/lockfile or tooling changes. No /analysis page, workbench,
CSS or selection.ts implementation exists. No commit, push or PR. STOP for review.

## GREEN verification evidence

After explicit approval, added the API module first; the unchanged contract probe
passed typecheck. Then added the client workbench, scoped CSS and thin /analysis
page. The probe SHA-256 remains
`dd6e2927f31ef7ca869b8a3ab2c04dd879c67c7d054916f0f0103f9f1b889a9e`.

Executed in the requested order after implementation, all **exit 0**:

1. `pnpm --dir apps/web typecheck`
2. `pnpm --dir apps/web lint`
3. `pnpm --dir apps/web build` (includes static `/analysis`)
4. `UV_CACHE_DIR=/private/tmp/liuliangchuhai-uv-cache make check`

The repository gate passed formatting, lint, types, architecture, all **318**
backend tests (242 unit, 39 contract, 35 integration, 2 acceptance), frontend
lint/typecheck/build and generated-contract drift. Tracked OpenAPI and generated
TypeScript stayed unchanged; drift checks generated only temporary candidates.

A temporary Node native-assertion check with deterministic fetch responses passed:
four-field request normalization without mutating the caller, required blanks
preventing fetch, exact 422/404/502/503/fallback messages, safe network/JSON errors,
no raw diagnostic leakage, and empty catalog/no-store behavior. No test framework,
dependency or persistent test file was added. The handler's separate in-flight ref
guard and the disabled button/fieldset were reviewed in source.

Light browser smoke observed `/analysis` loading, three backend product options
(柳州螺蛳粉, 梧州六堡茶, 桂林罗汉果), associated form labels, report placeholder,
and disabled submission with required inputs empty. After the continuation, the
temporary browser/server sessions were no longer available. Restarting the mock
API hit an automatic permission-review timeout; this was not a safety rejection.
Therefore a successful browser submission, transient submitting state, rendered
report, mobile layout and screenshots remain unverified manually. This optional
smoke was kept bounded as requested; no browser automation suite was introduced.

Final scope review: `git diff --check` passes. Only the approved constitution/AGENTS
guidance and three feature documents, the unchanged probe, and four implementation
files differ from HEAD. Core Principles and all AGENTS architecture/development
guidance are preserved. Backend/Domain/Application, OpenAPI/generated schema,
root page/layout, dependencies/lockfiles, providers/content/digital-human code and
Issue #5 are unchanged. Staging is empty. No commit, push or PR; stop for review.

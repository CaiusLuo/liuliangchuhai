# Feature Specification: Content Plan Contract

**Branch**: `feat/6-content-plan-contract` | **Date**: 2026-09-04
**Status**: Frozen V1; SPEC + PLAN + RED only
**Source**: [Issue #6](https://github.com/CaiusLuo/liuliangchuhai/issues/6) and the
user's authoritative frozen contract. Depends on merged Issue #2; parallel to #3.

## User scenarios and testing

### US1 — Stable materials for downstream content tools (P1)

A downstream tool needs shared selling points and distinct materials for images,
short videos, spoken presentations, and social captions. One validated plan gives
these consumers a stable boundary without generating or publishing media.

Independent acceptance: supply the existing Product, MarketContext, and
ProductMarketAnalysis plus ContentContext to a fake-backed use case; verify one
planner invocation with identical objects and the identical returned plan.
Direct invalid Domain construction must raise ValueError.

### US2 — Repeatable offline demo (P2)

A developer needs valid demo plans without credentials or third-party services.
Independent acceptance: repeated calls and fresh mock instances with identical
inputs produce equal valid plans, clearly marked demo/mock, with network blocked.

## Frozen requirements

### Input values

Reuse `Product`, `MarketContext`, and `ProductMarketAnalysis` unchanged.
The caller supplies all four validated inputs; there is no product lookup.

`ContentContext` is `@dataclass(frozen=True, slots=True)` with exactly:

| Field | Type | Validation |
| --- | --- | --- |
| target_language | str | Required; nonblank after stripping; no coercion |

V1 has no tone, platform, duration, aspect_ratio, style, hashtags, model,
temperature, provider, or locale metadata.

### Output value

`ContentGenerationPlan` is `@dataclass(frozen=True, slots=True)` with exactly:

| Field | Type | Meaning |
| --- | --- | --- |
| key_selling_points | tuple[str, ...] | Shared core selling points |
| image_prompt | str | Material for a future image-generation adapter |
| short_video_idea | str | Human/application-readable creative concept |
| short_video_prompt | str | Machine-oriented video-generation material |
| live_script | str | Spoken script for later digital-human/live use |
| social_caption | str | Social-media-ready caption copy |

The selling points must be a tuple with at least one item; every item must be a
nonblank str. Reject empty tuples, lists, bare strings, non-string items, and
blank/whitespace-only items. Every scalar must be a nonblank str. Reject all
non-string values without coercion. Invalid direct construction of either value
raises ValueError. Stripping detects blanks; no translation or normalization is
required by V1.

### Application-owned capability

Create a separate `ContentPlannerPort(Protocol)` with this business signature:

```python
async def create_content_plan(
    self,
    product: Product,
    market: MarketContext,
    analysis: ProductMarketAnalysis,
    context: ContentContext,
) -> ContentGenerationPlan: ...
```

Do not modify LLMPort or DigitalHumanPort. No messages, model, temperature,
max_tokens, response_format, vendor types, or status method is required here.
A future adapter may implement multiple ports; Application cannot rely on that.

### Thin use case

`CreateContentPlanUseCase(planner).execute(product, market, analysis, context)`
is async, forwards each exact object to the injected ContentPlannerPort exactly
once, and returns the exact ContentGenerationPlan result. It never inspects
recommendation/score, rewrites analysis, constructs prompts, translates, retries,
falls back, caches, or calls repositories, LLMPort, DigitalHumanPort, or HTTP APIs.

### Mock and failures

`MockContentPlannerAdapter` will implement the port with deterministic, obvious
demo material. It may derive strings from product.name, market.country, and
context.target_language; tests do not freeze full wording. No network, random,
current time, provider SDK, ranking/market algorithm, or score/recommendation
branching. It returns validated Domain values and requires no credentials.

V1 defines only Domain validation ValueError. There is no real provider and no
new error hierarchy: ContentPlannerUnavailable, InvalidContentPlannerResponse,
ProviderTimeout, and a generic provider framework are out of scope. The first
real integration will own any additional application/provider error contract.

### Downstream boundary and architecture

This issue ends at ContentGenerationPlan. Future ImageGeneratorPort may consume
image_prompt and return an image URL; VideoGeneratorPort may consume
short_video_prompt and return a video URL; DigitalHumanPort may consume
live_script and produce media. None of these integrations happens here.

Domain imports no outer layer; Application owns the port/use case and imports
only inward/standard-library abstractions. Infrastructure owns adapters;
Bootstrap alone selects concrete dependencies. Core modules must not import
FastAPI, Pydantic, httpx, requests, or provider SDKs. Keep existing checks intact.

## Success criteria and scope

- US1 covers exact frozen fields/types, valid and invalid construction, immutable
  values, provider-neutral async signature, four input identities, one call,
  and result identity regardless of recommendation or score.
- US2 covers a valid six-field result, repeatability across calls/instances,
  explicit demo/mock identification, and no external calls.
- RED fails for missing Issue #6 production modules; no skips, xfails, syntax
  errors, or placeholder production stubs. Record commands/results in tasks.md.
- Only these three feature documents and focused Issue #6 tests change this turn.
  Preserve Issue #3 specs/tests, shared fixtures, AGENTS.md, and constitution.
- Before future GREEN, reconcile phase authorization/governance after rebase;
  constitution 1.2.0 currently authorizes production only through Issue #2.

Out of scope: production code this turn; HTTP/Presentation/OpenAPI/frontend;
real LLMs, translation services, image/video/digital-human generation, publishing,
TikTok/social APIs, auth, persistence, RAG/vector DB, multi-agent workflows,
prompt optimization, generic provider abstractions, new dependencies, and Issues
#3/#5/#7. Do not commit, push, open a PR, or start GREEN.

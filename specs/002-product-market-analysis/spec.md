# Product-Market Analysis Contract

`MarketContext` is immutable: `country` is a required nonblank string;
`target_audience` and `market_notes` are optional nonblank strings.

`ProductMarketAnalysis` is immutable and contains:

- `recommendation`: `strong_fit`, `fit`, `caution`, or `not_recommended`
- `score`: integer from 0 through 100; a heuristic, not a forecast or probability
- `summary`: nonblank string
- `target_audiences`, `strengths`, `risks`, `cultural_advantages`,
  `marketing_suggestions`, `content_directions`: tuples of nonblank strings;
  empty tuples are valid

`LLMPort.analyze_product_market(product, market)` returns a valid analysis.
`AnalyzeProductUseCase` forwards the supplied objects to that port unchanged.
Provider outages and malformed provider results map to the application-owned,
distinct `LLMUnavailable` and `InvalidLLMResponse` failures.

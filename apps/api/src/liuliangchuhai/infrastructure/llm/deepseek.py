import json
from dataclasses import asdict
from typing import Any

import httpx

from liuliangchuhai.application.ports.llm_errors import InvalidLLMResponse, LLMUnavailable
from liuliangchuhai.application.ports.status import ProviderStatus
from liuliangchuhai.domain.market_analysis import (
    MarketContext,
    ProductMarketAnalysis,
    RecommendationLevel,
)
from liuliangchuhai.domain.product import Product

_BASE_URL = "https://api.deepseek.com"
_ANALYSIS_FIELDS = {
    "recommendation",
    "score",
    "summary",
    "target_audiences",
    "strengths",
    "risks",
    "cultural_advantages",
    "marketing_suggestions",
    "content_directions",
}
_ARRAY_FIELDS = (
    "target_audiences",
    "strengths",
    "risks",
    "cultural_advantages",
    "marketing_suggestions",
    "content_directions",
)
_SYSTEM_MESSAGE = """Analyze product-market fit as decision support.
Return exactly one JSON object and no markdown. The score is a heuristic from 0 through 100,
not a prediction, probability, or sales forecast. Use exactly these fields: recommendation,
score, summary, target_audiences, strengths, risks, cultural_advantages, marketing_suggestions,
content_directions. Every array must contain only strings. recommendation must be exactly one
of: strong_fit, fit, caution, not_recommended."""


def _reject_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_json(value: str) -> Any:
    return json.loads(
        value,
        parse_constant=_reject_constant,
        object_pairs_hook=_reject_duplicate_keys,
    )


class DeepSeekLLMAdapter:
    """DeepSeek HTTP adapter for the application-owned LLMPort."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._model = model
        self._timeout = httpx.Timeout(timeout_seconds)
        self._transport = transport
        self._headers = {"Authorization": f"Bearer {api_key}"}

    async def status(self) -> ProviderStatus:
        try:
            response = await self._request("GET", "/models")
            payload = _strict_json(response.text)
            models = payload["data"]
            available = isinstance(models, list) and any(
                isinstance(item, dict) and item.get("id") == self._model for item in models
            )
        except Exception:
            available = False
        return ProviderStatus(provider="deepseek", available=available)

    async def analyze_product_market(
        self, product: Product, market: MarketContext
    ) -> ProductMarketAnalysis:
        response = await self._request(
            "POST",
            "/chat/completions",
            json={
                "model": self._model,
                "stream": False,
                "response_format": {"type": "json_object"},
                "thinking": {"type": "disabled"},
                "messages": [
                    {"role": "system", "content": _SYSTEM_MESSAGE},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "product": asdict(product),
                                "market_context": asdict(market),
                            },
                            ensure_ascii=False,
                            default=str,
                        ),
                    },
                ],
            },
        )
        return self._parse_analysis(response.text)

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(
                    base_url=_BASE_URL,
                    headers=self._headers,
                    timeout=self._timeout,
                    transport=self._transport,
                ) as client:
                    response = await client.request(method, path, **kwargs)
            except (httpx.TimeoutException, httpx.ConnectError):
                if attempt == 0:
                    continue
                raise LLMUnavailable("DeepSeek request failed") from None
            except httpx.HTTPError:
                raise LLMUnavailable("DeepSeek request failed") from None

            if response.status_code in {500, 503} and attempt == 0:
                continue
            if not response.is_success:
                raise LLMUnavailable("DeepSeek request failed")
            return response
        raise LLMUnavailable("DeepSeek request failed")

    @staticmethod
    def _parse_analysis(response_body: str) -> ProductMarketAnalysis:
        try:
            envelope = _strict_json(response_body)
            choices = envelope["choices"]
            choice = choices[0]
            if choice["finish_reason"] != "stop":
                raise ValueError("DeepSeek output was incomplete")
            content = choice["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("DeepSeek output was empty")

            data = _strict_json(content)
            if not isinstance(data, dict) or set(data) != _ANALYSIS_FIELDS:
                raise ValueError("DeepSeek output fields do not match the analysis contract")
            if type(data["score"]) is not int:
                raise TypeError("score must be an integer")
            if not isinstance(data["summary"], str) or not data["summary"].strip():
                raise TypeError("summary must be a nonblank string")
            for field in _ARRAY_FIELDS:
                value = data[field]
                if not isinstance(value, list) or any(
                    not isinstance(item, str) or not item.strip() for item in value
                ):
                    raise TypeError(f"{field} must be an array of nonblank strings")

            return ProductMarketAnalysis(
                recommendation=RecommendationLevel(data["recommendation"]),
                score=data["score"],
                summary=data["summary"],
                target_audiences=tuple(data["target_audiences"]),
                strengths=tuple(data["strengths"]),
                risks=tuple(data["risks"]),
                cultural_advantages=tuple(data["cultural_advantages"]),
                marketing_suggestions=tuple(data["marketing_suggestions"]),
                content_directions=tuple(data["content_directions"]),
            )
        except (IndexError, KeyError, RecursionError, TypeError, ValueError):
            raise InvalidLLMResponse("DeepSeek returned invalid analysis output") from None

import inspect
from typing import Protocol, get_type_hints

from liuliangchuhai.application.ports.content_planner import ContentPlannerPort
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.domain.product import Product


def test_content_planner_is_a_separate_business_protocol() -> None:
    assert Protocol in ContentPlannerPort.__bases__
    assert LLMPort not in ContentPlannerPort.__mro__
    assert not hasattr(LLMPort, "create_content_plan")


def test_content_planner_exposes_only_the_frozen_async_domain_boundary() -> None:
    create = ContentPlannerPort.create_content_plan
    parameters = inspect.signature(create).parameters

    assert inspect.iscoroutinefunction(create)
    assert tuple(parameters) == ("self", "product", "market", "analysis", "context")
    assert all(p.default is inspect.Parameter.empty for p in parameters.values())
    assert get_type_hints(create) == {
        "product": Product,
        "market": MarketContext,
        "analysis": ProductMarketAnalysis,
        "context": ContentContext,
        "return": ContentGenerationPlan,
    }

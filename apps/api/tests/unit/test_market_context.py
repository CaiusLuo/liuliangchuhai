import pytest
from liuliangchuhai.domain.market_analysis import MarketContext


def test_minimal_market_context() -> None:
    market = MarketContext(country="Vietnam")

    assert market.country == "Vietnam"
    assert market.target_audience is None
    assert market.market_notes is None


def test_market_context_accepts_optional_fields() -> None:
    market = MarketContext(
        country="Thailand",
        target_audience="Students",
        market_notes="Explore small sample packs",
    )

    assert market.target_audience == "Students"
    assert market.market_notes == "Explore small sample packs"


def test_optional_fields_accept_explicit_none() -> None:
    market = MarketContext(country="Vietnam", target_audience=None, market_notes=None)

    assert market.target_audience is None
    assert market.market_notes is None


@pytest.mark.parametrize("country", ["", " \t\n", None, 123, True, ("Vietnam",)])
def test_market_context_rejects_invalid_country(country: object) -> None:
    with pytest.raises(ValueError):
        MarketContext(country=country)


@pytest.mark.parametrize("field", ["target_audience", "market_notes"])
@pytest.mark.parametrize("value", ["", " \t\n", 123, True, ("Students",)])
def test_market_context_rejects_invalid_optional_fields(field: str, value: object) -> None:
    with pytest.raises(ValueError):
        MarketContext(country="Vietnam", **{field: value})

from liuliangchuhai.domain.market_analysis import MarketContext, ProductMarketAnalysis
from liuliangchuhai.presentation.http.schemas import (
    ProductAnalysisRequest,
    ProductMarketAnalysisResponse,
)


def to_market_context(request: ProductAnalysisRequest) -> MarketContext:
    return MarketContext(
        country=request.country,
        target_audience=request.target_audience,
        market_notes=request.market_notes,
    )


def to_analysis_response(analysis: ProductMarketAnalysis) -> ProductMarketAnalysisResponse:
    return ProductMarketAnalysisResponse(
        recommendation=analysis.recommendation,
        score=analysis.score,
        summary=analysis.summary,
        target_audiences=list(analysis.target_audiences),
        strengths=list(analysis.strengths),
        risks=list(analysis.risks),
        cultural_advantages=list(analysis.cultural_advantages),
        marketing_suggestions=list(analysis.marketing_suggestions),
        content_directions=list(analysis.content_directions),
    )

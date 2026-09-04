from liuliangchuhai.domain.content_plan import ContentContext, ContentGenerationPlan
from liuliangchuhai.domain.market_analysis import ProductMarketAnalysis
from liuliangchuhai.presentation.http.content_plan_schemas import (
    ContentPlanAnalysis,
    ContentPlanRequest,
    ContentPlanResponse,
)


def to_product_market_analysis(analysis: ContentPlanAnalysis) -> ProductMarketAnalysis:
    return ProductMarketAnalysis(
        recommendation=analysis.recommendation,
        score=analysis.score,
        summary=analysis.summary,
        target_audiences=tuple(analysis.target_audiences),
        strengths=tuple(analysis.strengths),
        risks=tuple(analysis.risks),
        cultural_advantages=tuple(analysis.cultural_advantages),
        marketing_suggestions=tuple(analysis.marketing_suggestions),
        content_directions=tuple(analysis.content_directions),
    )


def to_content_context(request: ContentPlanRequest) -> ContentContext:
    return ContentContext(target_language=request.target_language)


def to_content_plan_response(plan: ContentGenerationPlan) -> ContentPlanResponse:
    return ContentPlanResponse(
        key_selling_points=list(plan.key_selling_points),
        image_prompt=plan.image_prompt,
        short_video_idea=plan.short_video_idea,
        short_video_prompt=plan.short_video_prompt,
        live_script=plan.live_script,
        social_caption=plan.social_caption,
    )

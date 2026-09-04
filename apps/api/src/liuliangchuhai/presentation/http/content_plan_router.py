import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from liuliangchuhai.application.use_cases.create_content_plan_by_id import (
    CreateContentPlanByIdUseCase,
)
from liuliangchuhai.application.use_cases.get_product import ProductNotFound
from liuliangchuhai.presentation.http.content_plan_mappers import (
    to_content_context,
    to_content_plan_response,
    to_product_market_analysis,
)
from liuliangchuhai.presentation.http.content_plan_schemas import (
    ContentPlanErrorResponse,
    ContentPlanRequest,
    ContentPlanResponse,
)
from liuliangchuhai.presentation.http.product_analysis_mappers import to_market_context
from liuliangchuhai.presentation.http.schemas import ProductNotFoundResponse

logger = logging.getLogger(__name__)


def create_content_plan_router(
    create_content_plan_by_id: CreateContentPlanByIdUseCase,
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/content-plan",
        response_model=ContentPlanResponse,
        operation_id="create_content_plan",
        responses={
            404: {"model": ProductNotFoundResponse, "description": "Product not found"},
            500: {"model": ContentPlanErrorResponse, "description": "Content planning failed"},
        },
    )
    async def create_content_plan(
        request: ContentPlanRequest,
    ) -> ContentPlanResponse | JSONResponse:
        market = to_market_context(request)
        analysis = to_product_market_analysis(request.analysis)
        context = to_content_context(request)
        try:
            plan = await create_content_plan_by_id.execute(
                request.product_id, market, analysis, context
            )
            return to_content_plan_response(plan)
        except ProductNotFound:
            return JSONResponse(
                status_code=404,
                content=ProductNotFoundResponse(
                    code="product_not_found", message="Product not found"
                ).model_dump(),
            )
        except Exception:
            logger.exception("Content planning failed")
            return JSONResponse(
                status_code=500,
                content=ContentPlanErrorResponse(
                    code="content_planning_failed",
                    message="Unable to create content plan. Please try again.",
                ).model_dump(),
            )

    return router

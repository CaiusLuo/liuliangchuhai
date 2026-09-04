from fastapi import APIRouter
from fastapi.responses import JSONResponse

from liuliangchuhai.application.ports.llm_errors import InvalidLLMResponse, LLMUnavailable
from liuliangchuhai.application.use_cases.analyze_product_by_id import AnalyzeProductByIdUseCase
from liuliangchuhai.application.use_cases.get_product import ProductNotFound
from liuliangchuhai.presentation.http.product_analysis_mappers import (
    to_analysis_response,
    to_market_context,
)
from liuliangchuhai.presentation.http.schemas import (
    ProductAnalysisErrorResponse,
    ProductAnalysisRequest,
    ProductMarketAnalysisResponse,
)


def create_product_analysis_router(analyze_product_by_id: AnalyzeProductByIdUseCase) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/product-analysis",
        response_model=ProductMarketAnalysisResponse,
        operation_id="analyze_product",
        responses={
            404: {"model": ProductAnalysisErrorResponse, "description": "Product not found"},
            502: {
                "model": ProductAnalysisErrorResponse,
                "description": "Analysis service returned an invalid response",
            },
            503: {
                "model": ProductAnalysisErrorResponse,
                "description": "Analysis service is temporarily unavailable",
            },
        },
    )
    async def analyze_product(
        request: ProductAnalysisRequest,
    ) -> ProductMarketAnalysisResponse | JSONResponse:
        market = to_market_context(request)
        try:
            analysis = await analyze_product_by_id.execute(request.product_id, market)
        except ProductNotFound:
            return JSONResponse(
                status_code=404,
                content=ProductAnalysisErrorResponse(
                    code="product_not_found", message="Product not found"
                ).model_dump(),
            )
        except LLMUnavailable:
            return JSONResponse(
                status_code=503,
                content=ProductAnalysisErrorResponse(
                    code="llm_unavailable", message="Analysis service is temporarily unavailable"
                ).model_dump(),
            )
        except InvalidLLMResponse:
            return JSONResponse(
                status_code=502,
                content=ProductAnalysisErrorResponse(
                    code="invalid_llm_response",
                    message="Analysis service returned an invalid response",
                ).model_dump(),
            )
        return to_analysis_response(analysis)

    return router

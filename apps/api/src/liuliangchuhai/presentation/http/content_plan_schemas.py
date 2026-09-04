from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from liuliangchuhai.presentation.http.schemas import (
    NonBlankString,
    ProductAnalysisRequest,
    ProductMarketAnalysisResponse,
)


class ContentPlanAnalysis(ProductMarketAnalysisResponse):
    model_config = ConfigDict(extra="forbid")


class ContentPlanRequest(ProductAnalysisRequest):
    target_language: NonBlankString
    analysis: ContentPlanAnalysis


class ContentPlanResponse(BaseModel):
    key_selling_points: Annotated[list[NonBlankString], Field(min_length=1)]
    image_prompt: NonBlankString
    short_video_idea: NonBlankString
    short_video_prompt: NonBlankString
    live_script: NonBlankString
    social_caption: NonBlankString


class ContentPlanErrorResponse(BaseModel):
    code: Literal["content_planning_failed"]
    message: Literal["Unable to create content plan. Please try again."]

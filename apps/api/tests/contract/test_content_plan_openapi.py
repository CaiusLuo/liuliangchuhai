import json
from pathlib import Path

import pytest
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings


@pytest.mark.parametrize("source", ["runtime", "committed"])
def test_content_plan_contract(source: str) -> None:
    if source == "runtime":
        document = create_app(Settings(_env_file=None)).openapi()
    else:
        document = json.loads((Path(__file__).resolve().parents[2] / "openapi.json").read_text())
    operation = document["paths"]["/content-plan"]["post"]
    schemas = document["components"]["schemas"]
    assert operation["operationId"] == "create_content_plan"
    assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ContentPlanRequest"
    )
    request = schemas["ContentPlanRequest"]
    assert set(request["required"]) == {"product_id", "country", "target_language", "analysis"}
    assert set(request["properties"]) == {
        "product_id",
        "country",
        "target_audience",
        "market_notes",
        "target_language",
        "analysis",
    }
    assert request["additionalProperties"] is False
    analysis = schemas["ContentPlanAnalysis"]
    assert analysis["properties"] == schemas["ProductMarketAnalysisResponse"]["properties"]
    assert analysis["required"] == schemas["ProductMarketAnalysisResponse"]["required"]
    assert analysis["additionalProperties"] is False
    assert set(operation["responses"]) == {"200", "404", "422", "500"}
    response = schemas["ContentPlanResponse"]
    assert (
        set(response["required"])
        == set(response["properties"])
        == {
            "key_selling_points",
            "image_prompt",
            "short_video_idea",
            "short_video_prompt",
            "live_script",
            "social_caption",
        }
    )
    assert response["properties"]["key_selling_points"]["minItems"] == 1
    assert operation["responses"]["404"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ProductNotFoundResponse"
    )
    assert operation["responses"]["500"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ContentPlanErrorResponse"
    )

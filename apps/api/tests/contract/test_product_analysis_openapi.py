import json
import subprocess
from pathlib import Path

import pytest
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings

ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(params=["runtime", "committed"])
def document(request: pytest.FixtureRequest) -> dict:
    if request.param == "runtime":
        return create_app(Settings(_env_file=None)).openapi()
    return json.loads((ROOT / "apps/api/openapi.json").read_text(encoding="utf-8"))


def _resolve(document: dict, schema: dict) -> dict:
    """Read local references without requiring a component name or inline layout."""
    while "$ref" in schema:
        reference = schema["$ref"]
        assert reference.startswith("#/"), f"Expected a local OpenAPI reference: {reference}"
        target = document
        for part in reference[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        schema = {**target, **{key: value for key, value in schema.items() if key != "$ref"}}
    if "allOf" in schema and len(schema["allOf"]) == 1:
        schema = {
            **_resolve(document, schema["allOf"][0]),
            **{key: value for key, value in schema.items() if key != "allOf"},
        }
    return schema


def _types(document: dict, schema: dict) -> set[str]:
    schema = _resolve(document, schema)
    for union in ("anyOf", "oneOf"):
        if union in schema:
            return set().union(*(_types(document, item) for item in schema[union]))
    value = schema["type"]
    types = {value} if isinstance(value, str) else set(value)
    return types | ({"null"} if schema.get("nullable") else set())


def _operation(document: dict) -> dict:
    assert "/product-analysis" in document["paths"], (
        "Product analysis endpoint missing from OpenAPI"
    )
    return document["paths"]["/product-analysis"]["post"]


def _response_schema(document: dict, status: str) -> dict:
    response = _resolve(document, _operation(document)["responses"][status])
    return _resolve(document, response["content"]["application/json"]["schema"])


def test_post_operation_and_request_are_documented(document: dict) -> None:
    operation = _operation(document)
    assert operation["operationId"] == "analyze_product"
    body = _resolve(document, operation["requestBody"])
    assert body["required"] is True
    request = _resolve(document, body["content"]["application/json"]["schema"])
    assert set(request["required"]) == {"product_id", "country"}
    assert set(request["properties"]) == {
        "product_id",
        "country",
        "target_audience",
        "market_notes",
    }
    for field in ("product_id", "country"):
        assert _types(document, request["properties"][field]) == {"string"}
    for field in ("target_audience", "market_notes"):
        assert _types(document, request["properties"][field]) == {"string", "null"}


def test_response_schema_and_recommendation_enum_are_documented(document: dict) -> None:
    response = _response_schema(document, "200")
    properties = response["properties"]
    collections = {
        "target_audiences",
        "strengths",
        "risks",
        "cultural_advantages",
        "marketing_suggestions",
        "content_directions",
    }
    assert set(properties) == {"recommendation", "score", "summary"} | collections
    assert set(response["required"]) == set(properties)
    score = _resolve(document, properties["score"])
    assert score["type"] == "integer"
    assert score["minimum"] == 0
    assert score["maximum"] == 100
    assert _types(document, properties["summary"]) == {"string"}
    for field in collections:
        collection = _resolve(document, properties[field])
        assert collection["type"] == "array"
        assert _types(document, collection["items"]) == {"string"}
    recommendation = _resolve(document, properties["recommendation"])
    assert recommendation["type"] == "string"
    assert set(recommendation["enum"]) == {"strong_fit", "fit", "caution", "not_recommended"}


def test_application_error_responses_are_documented(document: dict) -> None:
    validation = _response_schema(document, "422")
    assert "detail" in validation["properties"]
    assert _types(document, validation["properties"]["detail"]) == {"array"}
    for status in ("404", "502", "503"):
        error = _response_schema(document, status)
        assert set(error["required"]) == {"code", "message"}
        assert set(error["properties"]) == {"code", "message"}
        for field in ("code", "message"):
            assert _types(document, error["properties"][field]) == {"string"}


def test_generated_typescript_exposes_analysis_contract(tmp_path: Path) -> None:
    # Compile a consumer of the exported API types instead of matching generated text.
    generated = ROOT / "apps/web/src/api/generated/schema"
    consumer = tmp_path / "analysis-contract.ts"
    consumer.write_text(
        "import type { paths } from "
        + json.dumps(generated.as_posix())
        + ";\n"
        + """
type Operation = paths["/product-analysis"]["post"];
type Request = NonNullable<Operation["requestBody"]>["content"]["application/json"];
type Responses = Operation["responses"];
type Analysis = Responses[200]["content"]["application/json"];
const request: Request = {
    product_id: "luosifen", country: "Vietnam", target_audience: null, market_notes: null
};
const analysis: Analysis = {
    recommendation: "caution", score: 50, summary: "Demo heuristic",
    target_audiences: [], strengths: [], risks: [], cultural_advantages: [],
    marketing_suggestions: [], content_directions: []
};
const recommendations: Analysis["recommendation"][] = [
    "strong_fit", "fit", "caution", "not_recommended"
];
const missing: Responses[404]["content"]["application/json"] = {
    code: "product_not_found", message: "Product not found"
};
const unavailable: Responses[503]["content"]["application/json"] = {
    code: "llm_unavailable", message: "Analysis service is temporarily unavailable"
};
const invalid: Responses[502]["content"]["application/json"] = {
    code: "invalid_llm_response", message: "Analysis service returned an invalid response"
};
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "pnpm",
            "exec",
            "tsc",
            "--noEmit",
            "--strict",
            "--skipLibCheck",
            "--target",
            "ES2020",
            "--module",
            "commonjs",
            "--moduleResolution",
            "node",
            str(consumer),
        ],
        cwd=ROOT / "apps/web",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

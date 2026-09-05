import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def test_assistant_openapi_exposes_only_frozen_fields():
    document = json.loads((ROOT / "apps/api/openapi.json").read_text())
    operation = document["paths"]["/assistant/chat"]["post"]
    assert operation["operationId"] == "reply_to_customer"
    schemas = document["components"]["schemas"]
    request = schemas["AssistantChatRequest"]
    assert set(request["properties"]) == {"message", "product_id"}
    assert request["required"] == ["message"]
    assert request["additionalProperties"] is False
    assert request["properties"]["message"]["pattern"] == r"\S"
    response = schemas["AssistantChatResponse"]
    assert set(response["properties"]) == {"message", "suggested_action"}
    assert set(response["required"]) == {"message", "suggested_action"}
    assert {"type": "null"} in response["properties"]["suggested_action"]["anyOf"]
    assert set(schemas["AssistantSuggestedActionResponse"]["properties"]) == {"type", "product_id"}
    assert set(schemas["AssistantActionType"]["enum"]) == {"view_product", "start_analysis"}
    assert set(operation["responses"]) == {"200", "404", "422", "502", "503"}


def test_generated_typescript_assistant_consumer(tmp_path):
    consumer = tmp_path / "assistant-contract.ts"
    consumer.write_text(
        "import type { paths } from "
        + json.dumps((ROOT / "apps/web/src/api/generated/schema").as_posix())
        + ";\n"
        + """
type Operation = paths["/assistant/chat"]["post"];
type Request = NonNullable<Operation["requestBody"]>["content"]["application/json"];
type Reply = Operation["responses"][200]["content"]["application/json"];
const generic: Request = {message: "Question"};
const scoped: Request = {message: "Question", product_id: "tea"};
const nullable: Request = {message: "Question", product_id: null};
const plain: Reply = {message: "Answer", suggested_action: null};
const view: Reply = {
    message: "Answer", suggested_action: {type: "view_product", product_id: "tea"}};
const analysis: Reply = {
    message: "Answer", suggested_action: {type: "start_analysis", product_id: "tea"}};
// @ts-expect-error current message is required
const history: Request = {messages: []};
// @ts-expect-error action must be semantic
const url: Reply = {message: "Answer", suggested_action: {href: "/products/tea"}};
// @ts-expect-error at most one action
const multiple: Reply = {message: "Answer", suggested_action: []};
const missing: Operation["responses"][404]["content"]["application/json"] = {
    code: "product_not_found", message: "Product not found"
};
const unavailable: Operation["responses"][503]["content"]["application/json"] = {
    code: "assistant_unavailable", message: "Assistant service is temporarily unavailable"
};
const invalid: Operation["responses"][502]["content"]["application/json"] = {
    code: "invalid_assistant_response", message: "Assistant service returned an invalid response"
};
"""
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

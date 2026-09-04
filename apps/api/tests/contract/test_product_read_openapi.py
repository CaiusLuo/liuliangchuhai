import json
import subprocess
from pathlib import Path

import pytest
from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings

ROOT = Path(__file__).resolve().parents[4]
TEXT_FIELDS = {
    "id",
    "name",
    "category",
    "description",
    "origin",
    "cultural_background",
    "usage",
}
PRODUCT_FIELDS = TEXT_FIELDS | {"images", "ingredients", "price", "purchase_url"}


@pytest.fixture(params=["runtime", "committed"])
def document(request: pytest.FixtureRequest) -> dict:
    if request.param == "runtime":
        return create_app(Settings(_env_file=None)).openapi()
    return json.loads((ROOT / "apps/api/openapi.json").read_text(encoding="utf-8"))


def resolve(document: dict, schema: dict) -> dict:
    while "$ref" in schema:
        reference = schema["$ref"]
        assert reference.startswith("#/"), f"Expected a local reference: {reference}"
        target = document
        for part in reference[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        schema = {**target, **{key: value for key, value in schema.items() if key != "$ref"}}
    if "allOf" in schema and len(schema["allOf"]) == 1:
        return {
            **resolve(document, schema["allOf"][0]),
            **{key: value for key, value in schema.items() if key != "allOf"},
        }
    return schema


def types(document: dict, schema: dict) -> set[str]:
    schema = resolve(document, schema)
    for union in ("anyOf", "oneOf"):
        if union in schema:
            return set().union(*(types(document, item) for item in schema[union]))
    value = schema["type"]
    result = {value} if isinstance(value, str) else set(value)
    return result | ({"null"} if schema.get("nullable") else set())


def response_schema(document: dict, path: str, status: str) -> dict:
    assert path in document["paths"], f"GET {path} missing from OpenAPI"
    assert "get" in document["paths"][path]
    responses = document["paths"][path]["get"]["responses"]
    assert status in responses, f"GET {path} lacks documented {status}"
    response = resolve(document, responses[status])
    return resolve(document, response["content"]["application/json"]["schema"])


def assert_product_schema(document: dict, schema: dict) -> None:
    assert types(document, schema) == {"object"}
    properties = schema["properties"]
    assert set(properties) == PRODUCT_FIELDS
    assert set(schema["required"]) == PRODUCT_FIELDS
    for field in TEXT_FIELDS:
        assert types(document, properties[field]) == {"string"}
    for field in ("price", "purchase_url"):
        assert types(document, properties[field]) == {"string", "null"}
    for field in ("images", "ingredients"):
        array = resolve(document, properties[field])
        assert types(document, array) == {"array"}
        assert types(document, array["items"]) == {"string"}


def test_list_200_contains_only_items_of_product_response(document: dict) -> None:
    schema = response_schema(document, "/products", "200")
    assert types(document, schema) == {"object"}
    assert set(schema["properties"]) == {"items"}
    assert set(schema["required"]) == {"items"}
    items = resolve(document, schema["properties"]["items"])
    assert types(document, items) == {"array"}
    product = resolve(document, items["items"])
    assert_product_schema(document, product)
    detail = response_schema(document, "/products/{product_id}", "200")
    assert_product_schema(document, detail)


def test_detail_200_has_frozen_product_fields_and_string_price(document: dict) -> None:
    assert_product_schema(document, response_schema(document, "/products/{product_id}", "200"))


def test_detail_404_documents_public_product_not_found(document: dict) -> None:
    schema = response_schema(document, "/products/{product_id}", "404")
    assert types(document, schema) == {"object"}
    assert set(schema["properties"]) == {"code", "message"}
    assert set(schema["required"]) == {"code", "message"}
    for field in ("code", "message"):
        assert types(document, schema["properties"][field]) == {"string"}
    code = resolve(document, schema["properties"]["code"])
    assert code.get("enum", [code.get("const")]) == ["product_not_found"]


def test_generated_typescript_consumes_both_paths_and_models(tmp_path: Path) -> None:
    generated = ROOT / "apps/web/src/api/generated/schema"
    consumer = tmp_path / "product-read-contract.ts"
    consumer.write_text(
        "import type { paths, components } from "
        + json.dumps(generated.as_posix())
        + ";\n"
        + """
type ListGet = paths["/products"]["get"];
type DetailGet = paths["/products/{product_id}"]["get"];
type ProductResponse = components["schemas"]["ProductResponse"];
type ProductListResponse = components["schemas"]["ProductListResponse"];
type ListBody = ListGet["responses"][200]["content"]["application/json"];
type DetailBody = DetailGet["responses"][200]["content"]["application/json"];
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends
    (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
type ListModel = Assert<Equal<ListBody, ProductListResponse>>;
type DetailModel = Assert<Equal<DetailBody, ProductResponse>>;
type ItemModel = Assert<Equal<ProductListResponse["items"][number], ProductResponse>>;
type Price = Assert<Equal<ProductResponse["price"], string | null>>;
type Purchase = Assert<Equal<ProductResponse["purchase_url"], string | null>>;
type Images = Assert<Equal<ProductResponse["images"], string[]>>;
type Ingredients = Assert<Equal<ProductResponse["ingredients"], string[]>>;
type Fields = Assert<Equal<keyof ProductResponse,
    "id" | "name" | "category" | "description" | "origin" | "cultural_background" |
    "images" | "usage" | "ingredients" | "price" | "purchase_url">>;
type ListFields = Assert<Equal<keyof ProductListResponse, "items">>;
const product: ProductResponse = {
    id: "sample", name: "Name", category: "Category", description: "Description",
    origin: "Guangxi", cultural_background: "Background", images: [], usage: "Usage",
    ingredients: [], price: "12.50", purchase_url: null
};
const free: ProductResponse = { ...product, price: "0" };
const unpriced: ProductResponse = { ...product, price: null };
const list: ListBody = { items: [product, free, unpriced] };
const detail: DetailBody = product;
const params: DetailGet["parameters"]["path"] = { product_id: product.id };
const missing: DetailGet["responses"][404]["content"]["application/json"] = {
    code: "product_not_found", message: "Product not found"
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

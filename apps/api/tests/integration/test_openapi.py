from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings


def test_openapi_contains_health_contract() -> None:
    schema = create_app(Settings(_env_file=None)).openapi()

    health_operation = schema["paths"]["/health"]["get"]

    assert health_operation["operationId"] == "get_health"
    assert health_operation["responses"]["200"]["content"]["application/json"]
    assert "HealthResponse" in schema["components"]["schemas"]

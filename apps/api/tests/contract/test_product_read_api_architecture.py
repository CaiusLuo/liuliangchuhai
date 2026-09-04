import ast
import importlib.util
from pathlib import Path

import pytest


@pytest.mark.parametrize("name", ["products_router.py", "product_mappers.py"])
def test_product_read_presentation_has_no_repository_or_outer_imports(name: str) -> None:
    package = Path(__file__).resolve().parents[2] / "src" / "liuliangchuhai"
    path = package / "presentation" / "http" / name
    assert path.is_file(), f"Issue #17 Presentation module is missing: {name}"
    forbidden = (
        "liuliangchuhai.infrastructure",
        "liuliangchuhai.bootstrap",
        "liuliangchuhai.application.ports.product_repository",
    )
    violations: list[str] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = importlib.util.resolve_name(
                "." * node.level + (node.module or ""), "liuliangchuhai.presentation.http"
            )
            modules = [module, *(f"{module}.{alias.name}" for alias in node.names)]
        else:
            continue
        for module in modules:
            if (
                any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden)
                or module.rsplit(".", 1)[-1] in {"ProductRepository", "JsonProductRepository"}
                or (
                    name == "product_mappers.py" and module.startswith("liuliangchuhai.application")
                )
            ):
                violations.append(f"{name}:{node.lineno}: {module}")
    assert violations == []

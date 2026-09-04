import ast
import importlib.util
from pathlib import Path


def test_issue3_presentation_does_not_import_infrastructure_or_providers() -> None:
    package = Path(__file__).resolve().parents[2] / "src" / "liuliangchuhai"
    forbidden = (
        "liuliangchuhai.infrastructure",
        "liuliangchuhai.bootstrap",
        "openai",
        "anthropic",
        "httpx",
        "requests",
    )
    violations: list[str] = []
    for name in ("product_analysis_router.py", "product_analysis_mappers.py", "schemas.py"):
        path = package / "presentation" / "http" / name
        # Missing production files are asserted by the behavioral/contract tests.
        if not path.is_file():
            continue
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
                if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden):
                    violations.append(f"{name}:{node.lineno}: {module}")

    assert violations == []

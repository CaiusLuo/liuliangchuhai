import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "apps" / "api" / "src" / "liuliangchuhai"


def test_core_retains_existing_stdlib_and_inward_import_policy() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_core_imports.py")],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_issue2_core_modules_do_not_import_providers_or_outer_layers() -> None:
    # Existing gates enforce the global policy; this check is specific to Issue #2.
    issue2_modules = (
        "domain/market_analysis.py",
        "application/ports/llm.py",
        "application/ports/llm_errors.py",
        "application/use_cases/analyze_product.py",
    )
    forbidden = (
        "liuliangchuhai.infrastructure",
        "liuliangchuhai.presentation",
        "liuliangchuhai.bootstrap",
        "openai",
        "anthropic",
        "fastapi",
        "httpx",
        "requests",
        "http",
        "urllib",
    )
    violations: list[str] = []
    for relative in issue2_modules:
        path = PACKAGE / relative
        # Missing contracts cause RED in the behavioral tests, not this import check.
        if not path.is_file():
            continue
        package_name = ".".join(("liuliangchuhai", *Path(relative).parent.parts))
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                module = importlib.util.resolve_name(
                    "." * node.level + (node.module or ""), package_name
                )
                modules = [module, *(f"{module}.{alias.name}" for alias in node.names)]
            else:
                continue
            for module in modules:
                if any(module == prefix or module.startswith(f"{prefix}.") for prefix in forbidden):
                    violations.append(f"{relative}:{node.lineno}: {module}")

    assert violations == []

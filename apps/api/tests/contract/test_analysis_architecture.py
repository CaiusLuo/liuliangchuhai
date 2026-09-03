import ast
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


def test_core_contains_no_http_or_json_filesystem_imports() -> None:
    forbidden = {"http", "urllib", "socket", "json", "pathlib"}
    violations: list[str] = []
    for layer in ("domain", "application"):
        for path in (PACKAGE / layer).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                    modules = [node.module]
                else:
                    continue
                for module in modules:
                    if module.split(".")[0] in forbidden:
                        violations.append(f"{path.relative_to(PACKAGE)}:{node.lineno}: {module}")

    assert violations == []

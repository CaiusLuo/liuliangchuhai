"""Enforce the standard-library-only policy for the backend core."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "apps" / "api" / "src" / "liuliangchuhai"
CORE_PACKAGE = "liuliangchuhai"


def _is_allowed(layer: str, module: str) -> bool:
    top_level = module.split(".", 1)[0]
    if top_level in sys.stdlib_module_names:
        return True
    if layer == "domain":
        return module == f"{CORE_PACKAGE}.domain" or module.startswith(f"{CORE_PACKAGE}.domain.")
    return module in {
        f"{CORE_PACKAGE}.domain",
        f"{CORE_PACKAGE}.application",
    } or module.startswith((f"{CORE_PACKAGE}.domain.", f"{CORE_PACKAGE}.application."))


def find_violations(package_root: Path = PACKAGE_ROOT) -> list[str]:
    violations: list[str] = []
    for layer in ("domain", "application"):
        layer_root = package_root / layer
        for path in sorted(layer_root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                modules: list[str]
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level or node.module is None:
                        continue
                    modules = [node.module]
                else:
                    continue
                for module in modules:
                    if not _is_allowed(layer, module):
                        relative_path = path.relative_to(package_root)
                        violations.append(f"{relative_path}:{node.lineno}: {module}")
    return violations


def main() -> None:
    violations = find_violations()
    if violations:
        print("Core import policy violations:")
        print("\n".join(f"- {violation}" for violation in violations))
        raise SystemExit(1)
    print("Core import policy passed.")


if __name__ == "__main__":
    main()

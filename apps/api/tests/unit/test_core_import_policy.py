import importlib.util
from pathlib import Path


def _load_policy_module():
    script = Path(__file__).parents[4] / "scripts" / "check_core_imports.py"
    spec = importlib.util.spec_from_file_location("core_import_policy", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


find_violations = _load_policy_module().find_violations


def test_core_import_policy_rejects_unknown_third_party_modules(tmp_path: Path) -> None:
    application = tmp_path / "application"
    application.mkdir()
    (application / "bad.py").write_text("import future_vendor_sdk\n", encoding="utf-8")

    violations = find_violations(tmp_path)

    assert violations == ["application/bad.py:1: future_vendor_sdk"]


def test_core_import_policy_allows_stdlib_and_core_modules(tmp_path: Path) -> None:
    domain = tmp_path / "domain"
    application = tmp_path / "application"
    domain.mkdir()
    application.mkdir()
    (domain / "models.py").write_text("from dataclasses import dataclass\n", encoding="utf-8")
    (application / "use_case.py").write_text(
        "from liuliangchuhai.domain.models import Thing\n"
        "from liuliangchuhai.application.ports import Port\n",
        encoding="utf-8",
    )

    assert find_violations(tmp_path) == []

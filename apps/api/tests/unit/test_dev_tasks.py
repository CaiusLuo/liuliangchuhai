import importlib.util
from pathlib import Path


def _load_dev_module():
    script = Path(__file__).parents[4] / "scripts" / "dev.py"
    spec = importlib.util.spec_from_file_location("dev_tasks", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dev = _load_dev_module()


def test_resolve_command_uses_path_lookup(monkeypatch) -> None:
    monkeypatch.setattr(dev.shutil, "which", lambda name: "/tools/pnpm" if name == "pnpm" else None)

    assert dev.resolve_command("pnpm") == "/tools/pnpm"


def test_resolve_command_falls_back_to_windows_shims(monkeypatch) -> None:
    monkeypatch.setattr(dev.os, "name", "nt")
    lookups: list[str] = []

    def fake_which(name: str) -> str | None:
        lookups.append(name)
        return r"C:\tools\pnpm.CMD" if name == "pnpm.cmd" else None

    monkeypatch.setattr(dev.shutil, "which", fake_which)

    assert dev.resolve_command("pnpm") == r"C:\tools\pnpm.CMD"
    assert lookups == ["pnpm", "pnpm.cmd"]


def test_all_pnpm_commands_use_resolved_executable(monkeypatch) -> None:
    monkeypatch.setattr(dev, "resolve_command", lambda name: "/tools/pnpm.cmd")

    assert dev.pnpm_command("install", "--frozen-lockfile") == [
        "/tools/pnpm.cmd",
        "install",
        "--frozen-lockfile",
    ]


def test_bootstrap_copies_missing_env_files_without_overwriting_existing_files(
    monkeypatch, tmp_path: Path
) -> None:
    api_dir = tmp_path / "apps" / "api"
    web_dir = tmp_path / "apps" / "web"
    api_dir.mkdir(parents=True)
    web_dir.mkdir(parents=True)
    (api_dir / ".env.example").write_text("backend-default\n", encoding="utf-8")
    (web_dir / ".env.example").write_text("frontend-default\n", encoding="utf-8")

    monkeypatch.setattr(dev, "ROOT", tmp_path)
    monkeypatch.setattr(dev, "API_DIR", api_dir)
    monkeypatch.setattr(dev, "WEB_DIR", web_dir)
    monkeypatch.setattr(dev, "require_tools", lambda *names: None)
    monkeypatch.setattr(dev, "run", lambda *args, **kwargs: None)

    dev.bootstrap()
    assert (api_dir / ".env").read_text(encoding="utf-8") == "backend-default\n"
    assert (web_dir / ".env.local").read_text(encoding="utf-8") == "frontend-default\n"

    (api_dir / ".env").write_text("developer-value\n", encoding="utf-8")
    dev.bootstrap()

    assert (api_dir / ".env").read_text(encoding="utf-8") == "developer-value\n"

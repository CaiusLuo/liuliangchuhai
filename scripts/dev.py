"""Cross-platform developer task runner; Makefile aliases delegate here."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
WEB_DIR = ROOT / "apps" / "web"
API_TESTS = API_DIR / "tests"
OPENAPI_FILE = API_DIR / "openapi.json"
CLIENT_FILE = WEB_DIR / "src" / "api" / "generated" / "schema.ts"
RUFF_PATHS = [API_DIR / "src", API_TESTS, ROOT / "scripts" / "dev.py"]
GENERATED_WARNING = "// DO NOT EDIT MANUALLY. Generated from apps/api/openapi.json.\n"


def _display(command: Sequence[str]) -> str:
    return " ".join(command)


def run(command: Sequence[str], *, cwd: Path = ROOT) -> None:
    print(f"$ {_display(command)}", flush=True)
    subprocess.run(list(command), cwd=cwd, check=True)


def require_tools(*names: str) -> None:
    missing = [name for name in names if shutil.which(name) is None]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"Missing required tool(s): {joined}")


def uv_run(*args: str) -> list[str]:
    return ["uv", "run", "--project", str(API_DIR), *args]


def backend_paths() -> list[str]:
    return [str(path) for path in RUFF_PATHS]


def bootstrap() -> None:
    require_tools("uv", "pnpm")
    run(["uv", "sync", "--project", str(API_DIR), "--all-groups", "--locked"])
    run(["pnpm", "install", "--frozen-lockfile"], cwd=WEB_DIR)


def dev_api() -> None:
    require_tools("uv")
    run(
        uv_run(
            "uvicorn",
            "liuliangchuhai.bootstrap.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        )
    )


def dev_web() -> None:
    require_tools("pnpm")
    run(["pnpm", "dev"], cwd=WEB_DIR)


def dev() -> None:
    require_tools("uv", "pnpm")
    commands = [
        (
            uv_run(
                "uvicorn",
                "liuliangchuhai.bootstrap.main:app",
                "--reload",
                "--port",
                "8000",
            ),
            ROOT,
        ),
        (["pnpm", "dev"], WEB_DIR),
    ]
    processes: list[subprocess.Popen[bytes]] = []
    try:
        for command, cwd in commands:
            print(f"$ {_display(command)}", flush=True)
            processes.append(subprocess.Popen(command, cwd=cwd))
        while all(process.poll() is None for process in processes):
            time.sleep(0.25)
        failed = next((process.returncode for process in processes if process.returncode), 0)
        if failed:
            raise subprocess.CalledProcessError(failed, "development server")
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def format_code() -> None:
    run(
        uv_run(
            "ruff",
            "check",
            "--fix",
            "--config",
            str(API_DIR / "pyproject.toml"),
            *backend_paths(),
        )
    )
    run(uv_run("ruff", "format", "--config", str(API_DIR / "pyproject.toml"), *backend_paths()))


def format_check() -> None:
    run(
        uv_run(
            "ruff",
            "format",
            "--check",
            "--config",
            str(API_DIR / "pyproject.toml"),
            *backend_paths(),
        )
    )


def lint() -> None:
    run(uv_run("ruff", "check", "--config", str(API_DIR / "pyproject.toml"), *backend_paths()))


def typecheck() -> None:
    run(uv_run("mypy", str(API_DIR / "src")))


def architecture_check() -> None:
    run(uv_run("lint-imports", "--config", str(API_DIR / "pyproject.toml")))


def test_path(path: Path) -> None:
    run(uv_run("pytest", str(path), "-q"))


def test() -> None:
    test_path(API_TESTS)


def test_unit() -> None:
    test_path(API_TESTS / "unit")


def test_contract() -> None:
    test_path(API_TESTS / "contract")


def test_integration() -> None:
    test_path(API_TESTS / "integration")


def test_acceptance() -> None:
    test_path(API_TESTS / "acceptance")


def frontend_lint() -> None:
    run(["pnpm", "lint"], cwd=WEB_DIR)


def frontend_typecheck() -> None:
    run(["pnpm", "typecheck"], cwd=WEB_DIR)


def generate_openapi(destination: Path = OPENAPI_FILE) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(
        uv_run(
            "python",
            "-m",
            "liuliangchuhai.bootstrap.openapi",
            "--output",
            str(destination),
        )
    )


def generate_client(source: Path = OPENAPI_FILE, destination: Path = CLIENT_FILE) -> None:
    if not source.is_file():
        raise SystemExit(f"OpenAPI source does not exist: {source}. Run the openapi task first.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "pnpm",
            "exec",
            "openapi-typescript",
            str(source),
            "--output",
            str(destination),
        ],
        cwd=WEB_DIR,
    )
    generated = destination.read_text(encoding="utf-8")
    if not generated.startswith(GENERATED_WARNING):
        destination.write_text(GENERATED_WARNING + generated, encoding="utf-8")


def generated_check() -> None:
    with tempfile.TemporaryDirectory(prefix="liuliangchuhai-generated-") as temporary:
        temporary_path = Path(temporary)
        openapi_candidate = temporary_path / "openapi.json"
        client_candidate = temporary_path / "schema.ts"
        generate_openapi(openapi_candidate)
        generate_client(openapi_candidate, client_candidate)

        stale: list[Path] = []
        for committed, candidate in (
            (OPENAPI_FILE, openapi_candidate),
            (CLIENT_FILE, client_candidate),
        ):
            if not committed.is_file() or not filecmp.cmp(committed, candidate, shallow=False):
                stale.append(committed.relative_to(ROOT))
        if stale:
            names = ", ".join(str(path) for path in stale)
            raise SystemExit(f"Generated artifacts are stale: {names}. Run openapi and client-gen.")


def check() -> None:
    require_tools("uv", "pnpm")
    stages: list[tuple[str, Callable[[], None]]] = [
        ("formatting check", format_check),
        ("backend lint", lint),
        ("backend typecheck", typecheck),
        ("architecture boundaries", architecture_check),
        ("unit tests", test_unit),
        ("contract tests", test_contract),
        ("integration tests", test_integration),
        ("acceptance tests", test_acceptance),
        ("frontend lint", frontend_lint),
        ("frontend typecheck", frontend_typecheck),
        ("generated contract drift", generated_check),
    ]
    for name, stage in stages:
        print(f"\n==> {name}", flush=True)
        stage()
    print("\nAll checks passed.", flush=True)


def clean() -> None:
    directories = [
        ROOT / ".import_linter_cache",
        ROOT / ".mypy_cache",
        ROOT / ".ruff_cache",
        API_DIR / ".pytest_cache",
        API_DIR / ".mypy_cache",
        API_DIR / ".ruff_cache",
        WEB_DIR / ".next",
    ]
    for cache_root in (API_DIR / "src", API_TESTS, ROOT / "scripts"):
        directories.extend(cache_root.rglob("__pycache__"))
    for directory in sorted(set(directories), key=lambda path: len(path.parts), reverse=True):
        if directory.is_dir():
            shutil.rmtree(directory)
            print(f"removed {directory.relative_to(ROOT)}")
    for file_path in (WEB_DIR / "tsconfig.tsbuildinfo",):
        if file_path.is_file():
            file_path.unlink()
            print(f"removed {file_path.relative_to(ROOT)}")


TASKS: dict[str, tuple[Callable[[], None], str]] = {
    "bootstrap": (bootstrap, "Install locked backend and frontend dependencies"),
    "dev": (dev, "Run API and web development servers"),
    "dev-api": (dev_api, "Run the FastAPI development server"),
    "dev-web": (dev_web, "Run the Next.js development server"),
    "test": (test, "Run all backend tests"),
    "test-unit": (test_unit, "Run backend unit tests"),
    "test-contract": (test_contract, "Run provider and ownership contract tests"),
    "test-integration": (test_integration, "Run API integration tests"),
    "test-acceptance": (test_acceptance, "Run mock-only acceptance tests"),
    "lint": (lint, "Lint backend Python"),
    "format": (format_code, "Format and auto-fix backend Python"),
    "typecheck": (typecheck, "Type-check backend Python"),
    "architecture-check": (architecture_check, "Enforce backend import boundaries"),
    "openapi": (generate_openapi, "Generate apps/api/openapi.json"),
    "client-gen": (generate_client, "Generate the TypeScript API contract"),
    "generated-check": (generated_check, "Check OpenAPI and client drift"),
    "check": (check, "Run the complete non-mutating quality gate"),
    "clean": (clean, "Remove build and tool caches"),
}


def print_help() -> None:
    width = max(len(name) for name in TASKS)
    print("Available tasks:")
    for name, (_, description) in TASKS.items():
        print(f"  {name:<{width}}  {description}")


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("task", nargs="?", default="help")
    args = parser.parse_args()
    if args.task == "help":
        print_help()
        return
    task = TASKS.get(args.task)
    if task is None:
        print_help()
        raise SystemExit(f"\nUnknown task: {args.task}")
    task[0]()


if __name__ == "__main__":
    main()

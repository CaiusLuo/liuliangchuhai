import argparse
import json
from pathlib import Path

from liuliangchuhai.bootstrap.app import create_app
from liuliangchuhai.bootstrap.settings import Settings


def export_openapi(destination: Path) -> None:
    schema = create_app(Settings.model_validate({})).openapi()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the deterministic OpenAPI schema.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export_openapi(args.output.resolve())


if __name__ == "__main__":
    main()

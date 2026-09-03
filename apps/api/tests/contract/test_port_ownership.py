from pathlib import Path


def test_provider_ports_are_owned_by_application_layer() -> None:
    package_root = Path(__file__).parents[2] / "src" / "liuliangchuhai"

    assert (package_root / "application" / "ports" / "llm.py").is_file()
    assert (package_root / "application" / "ports" / "digital_human.py").is_file()
    assert not (package_root / "infrastructure" / "ports").exists()

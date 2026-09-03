.PHONY: bootstrap dev dev-api dev-web test test-unit test-contract test-integration test-acceptance lint format typecheck architecture-check openapi client-gen generated-check check clean help

bootstrap dev dev-api dev-web test test-unit test-contract test-integration test-acceptance lint format typecheck architecture-check openapi client-gen generated-check check clean help:
	uv run python scripts/dev.py $@

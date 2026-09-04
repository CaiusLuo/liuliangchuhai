# Contributing

## Contributor workflow

External contributors should use this flow:

1. Pick or receive a scoped GitHub Issue.
2. Fork the repository and create a feature branch for that Issue.
3. Keep changes inside the Issue's allowed scope and architecture boundaries.
4. Run the required focused checks and `make check` when applicable.
5. Open a pull request that links the Issue and includes concise verification evidence.
6. Wait for CI and maintainer review.
7. Do not self-merge the upstream pull request. Only `@CaiusLuo` performs merges into `main`.

Implementation work does not require upstream write access. Contributors should not be granted write, maintain, or admin access merely to submit changes.

## Architecture ownership

`@CaiusLuo` owns the repository contracts and merge decisions. Contributors must stop and ask before changing frozen Domain/Application/public API contracts or expanding an Issue beyond its stated scope.

A passing CI run does not authorize merge by itself. The maintainer reviews the final diff and decides whether to merge.

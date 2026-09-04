## Maintainer Merge Policy

- [ ] I understand that contributors must not self-merge this PR into `main`.
- [ ] I will wait for `@CaiusLuo` to review and perform the merge after required checks pass.

## Related Issue

Closes #<!-- replace with issue number, e.g. Closes #9 -->

<!-- One PR should normally solve one primary Issue. -->

## Summary

<!--
In 2-4 lines, explain what you implemented and why.
Example:
- Resolve pnpm executable correctly on Windows.
- Reuse the same command resolution for every pnpm invocation in scripts/dev.py.
-->

## Changes

<!-- List the important implementation changes. Keep this focused on the linked Issue. -->

- 
- 

## Testing

<!-- Check what you actually ran. Add commands/results below when useful. -->

- [ ] Relevant unit tests pass
- [ ] Relevant contract/integration tests pass
- [ ] `make check` passes on macOS/Linux, or `uv run python scripts/dev.py check` on Windows
- [ ] GitHub Actions required by this Issue pass

Test commands / important output:

```text
# paste concise verification output here, or write N/A
```

## Evidence

<!--
Add evidence required by the Issue, for example:
- screenshots for UI changes
- CI run/result for tooling fixes
- generated output/provider result for integrations
Write N/A when the Issue does not require visual/runtime evidence.
-->

N/A

## Architecture Impact

Check exactly what applies:

- [ ] None
- [ ] Public API contract changed
- [ ] Domain/Application contract changed
- [ ] Infrastructure/provider wiring changed
- [ ] Development tooling / CI changed
- [ ] Other architecture-related change

<!-- If anything except None is checked, explain the impact below. -->

Architecture notes: N/A

## Scope & Safety Check

- [ ] This PR addresses the linked Issue and does not include unrelated feature work.
- [ ] I did not add unrelated refactors or dependency upgrades.
- [ ] I followed the Issue's Allowed Changes / Out of Scope constraints.
- [ ] I did not commit secrets, API keys, `.env`, or other local-only files.
- [ ] Generated API files, if affected, were regenerated rather than edited manually.
- [ ] I reviewed my own diff before requesting review.

## Reviewer Notes

<!--
Optional: point the maintainer to anything that deserves extra attention,
such as a trade-off, uncertain behavior, or file that should be reviewed first.
Write N/A if there is nothing special.
-->

N/A

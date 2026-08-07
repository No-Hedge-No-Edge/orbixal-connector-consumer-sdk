# Consumer SDK Release and Compatibility Policy

This SDK is the agent-facing contract for Runtime Service connector access.

## Versioning

Use semantic versioning.

* Patch: bug fixes, docs, generated type corrections that do not change runtime payloads.
* Minor: additive helpers, new generated action wrappers, new exception subclasses for existing runtime codes.
* Major: breaking method signatures, removed public exports, or incompatible runtime payload changes.

## Runtime Compatibility

The SDK targets Runtime Service `1.x` while canonical schemas remain on the
`2026-01` connector platform contract.

Compatibility rules:

* SDK clients must keep emitting canonical `/runtime/execute` payloads.
* New runtime response fields must be ignored by older SDK clients unless required.
* New SDK helpers must be additive and route through the existing runtime operations:
  `describe`, `test_connection`, `list_resources`, `read`, and `query`.
* Consumer SDK releases should include contract tests against canonical Runtime Service schemas.

## Schema Sync

Generated models are synced from `orbixal-data-connector/schemas`:

```bash
uv run python scripts/sync_contract_models.py --check
```

Generated first-party action wrappers are synced from published manifest snapshots:

```bash
uv run python scripts/generate_action_wrappers.py \
  --manifest-root /Users/tgall/orbixal-first-party-connectors/dist
```

Generated first-party wrappers stay in `connector_consumer_sdk.first_party_actions`.
The top-level package exports only curated stable wrappers from
`connector_consumer_sdk.actions`. This keeps broad manifest-generated churn from
becoming top-level SDK API churn, while still making every approved first-party
action importable for internal agents that want generated coverage.

## Release Gate

Before publishing:

1. Run unit tests.
2. Run schema sync check.
3. Generate action wrappers from current approved manifests.
4. Review generated wrapper diffs for public API churn.
5. Build package artifacts.
6. Publish only from a tagged release.

## Publishing

Initial releases should publish to a private package registry, such as an
internal index or GitHub Packages. Public PyPI publishing should wait until the
public third-party connector program is ready and the support/deprecation process
is staffed.

Release automation must use short-lived trusted publishing credentials where the
registry supports them. For PyPI, use Trusted Publishing/OIDC. For GitHub
Packages or an internal registry, use GitHub Actions environment-scoped secrets
or workload identity, not checked-in tokens or developer-local credentials.

## Deprecation

Deprecated helpers should stay for one minor release unless there is a security issue.
Direct instance methods remain available for trusted internal callers, but docs should keep
alias-first bound access as the default agent path.

# Upgrade plan — book-competition-data

Current state: **7/10** (pass 1: 5 -> 6.5; pass 2: 6.5 -> 7). Offline contract, adapters and CLI are tested and linted in CI; live capture, source permission and consumers remain unverified by design.

## Backlog

- P0: Push this branch and confirm the new GitHub Actions `CI` workflow is green on both Python versions.
- P1: Strengthen drift markers for `nasa-prizes-innovation-challenges`, `drivendata-data-science-competitions` — their `required_markers` are only fragments of the title, so a challenge or error page that repeats the title would pass. Pick body phrases from a captured page (needs a reviewed live capture; not done offline).
- P1: Replace the copy of `cli.py`/`capture.py` scaffolding shared by the sibling `book-*-data` repos with the shared runtime package once it is independently installable (README gate 3).
- P2: NASA Space Apps status flips to `unknown` after 2026-11-15; add the 2027 intake as a new source record ID when announced.
- P2: Add a live-capture smoke job only behind an explicit manual trigger and reviewed source permission (never on push).

## Done in this pass (pass 1)

- Added `.github/workflows/ci.yml`: `ruff check`, `pytest` and an offline CLI smoke (`contract`, `validate demo.json`, `demo --open-only`) on Python 3.10 and 3.13.
- Added `[project.optional-dependencies] dev` (pytest, pinned ruff), `[tool.ruff]` and `[tool.pytest.ini_options]` to `pyproject.toml`; fixed import-order lint.
- Added `tests/test_registry.py`: `sources.json` ↔ packaged `source*.json` consistency (product, domain, category in contract, https URLs, interval), source-ID selector rejects traversal/unknown IDs, every marker-driven adapter normalizes a synthetic page into a valid live record and rejects a challenge page, JSON adapters reject non-object payloads, CLI `validate` exit codes do not echo input.
- `source.json` duplicates `source-nasa-space-apps-2026.json` byte-for-byte; the registry test now pins that every packaged config is registered and file-named by ID.

## Done in this pass (pass 2)

- Kept both `source.json` (registry `policy_file`, no-flag CLI default, possibly read by the
  shared runtime) and `source-nasa-space-apps-2026.json` (`--source-id` lookup) instead of
  deleting one, and added a byte-equality test plus `source_config()` ==
  `source_config("nasa-space-apps-2026")`, so drift fails CI. README documents the rule.
- Drift markers for the two weak sources were left unchanged: stronger phrases need a
  reviewed live capture.

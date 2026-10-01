# Upgrade plan — book-competition-data

Current state: **7.5/10** (pass 1: 5 -> 6.5; pass 2: 6.5 -> 7; pass 3: 7 -> 7.5; pass 4: unchanged). Offline contract, adapters and CLI have offline tests and lint wired into CI (runs not yet confirmed green, see P0); live capture, source permission and consumers remain unverified by design.

## Backlog

- P0: Confirm GitHub Actions `CI` is green on `claude/untitled-session-bhlj06`. The branch is pushed, but every run so far ended within ~5 s with no job logs (runner never started, not a test failure); check the account's Actions/billing settings, then re-run.
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
- Drift guard: the HTML text extractor now also ignores `<noscript>` and `<svg>` (matching
  the sibling creator/deal/learning/mobility/paid-study/partnership/startup adapters), so
  markers hidden there cannot pass a challenge page; `tests/test_text_extraction.py`.

## Done in this pass (pass 3)

- Score: 7 -> 7.5.
- CASSINI status used the UTC calendar date for a Brussels-time window (31 Oct 23:30Z, already 1 Nov in Brussels, showed `open`); it now compares instants 2026-09-01T00:00+02:00 .. 2026-11-01T00:00+01:00. NASA Space Apps bound moved from 23:59Z to 2026-11-16T00:00Z. A naive `checked_at` now fails with ValueError instead of being read as UTC or raising TypeError.
- Shared `cli.py` (same edit in all 13 sibling copies): `validate` now rejects NaN, ±Infinity and overflowing literals such as `1e400` (Python's json turns them into non-finite floats that JSON Schema `number` accepted); `timestamp` normalises fractional seconds so Python 3.10 accepts the same RFC3339 values as 3.11+ (it rejected e.g. `.1Z`) and only ASCII digits match; a trailing-dot `example.org.` host can no longer be claimed `live`.
- `tests/test_shared_cli.py` (byte-identical in all 13 repos) pins this repo's `cli.py` sha256 (three variants: base, +`contract --version`, +benefit availability) so a one-repo edit fails CI, and covers the fixes above across UTC/+07:00/-04:00 offsets. To change `cli.py`: edit every copy of the variant, then update `CLI_SHA256` in all 13 copies of the test.
- Not done (needs a reviewed live capture, so left blocked): stronger drift markers and any page-phrase extraction; no page phrases were invented.

## Done in this pass (pass 4: edge cases)

- Shared `cli.py` (all 13 copies, pins updated in `tests/test_shared_cli.py`):
  - `validate` accepted `" "` or a lone U+200B/BOM/soft hyphen as `id`,
    `title`, `provider` or `eligibility_text` (schema `minLength: 1` counts
    invisible characters); these are now rejected as blank.
  - Record ids that differ only by invisible characters or surrounding
    whitespace (`"x"` vs `"​x "`) are now reported as duplicates.
  - `demo --query` compared raw `casefold()` strings, so Thai SARA AM (`ำ`)
    did not match NIKHAHIT + SARA AA (either mark order), Thai digits did not
    match ASCII (`๒๕๖๙` vs `2569`), and full-width Latin (`ＵＫ`) or a stray
    zero-width space never matched; both sides are now NFKC-folded.
  - Verified: new `TextNormalisationTest` (all cases fail on the old code);
    full suite on Python 3.10 and 3.11; ruff 0.15.8 + 0.16.9.

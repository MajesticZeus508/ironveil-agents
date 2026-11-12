# Reliability work checkpoint — 2026-11-09

## Current reading guide

Historical concurrency implementation ledger. Current staging **0.1.4** was
rechecked active/latest; latest five-run evaluation achieved 28/35 analyses,
not uniformly 7/7. Fresh CLI 14 passed/one SDK skip; see
[team evaluation](../EVALUATION.md) and [verification](VERIFICATION.md).

## Historical finalized checkpoint — 2026-11-10 UTC

0.1.2 concurrency-two source was published and hosted acceptance completed;
AMS automatically rebuilt it as **0.1.3**, now active/latest with the same source
bundle `25236cc9-0f35-4ddf-94f9-5f765f1f434e`. All 15 tests passed in prior
managed verification. Latest operator full-chain run completed 7/7 recommendations
and five files in 206.181s; Recommendation child took 174.454s including startup.
See [verification](VERIFICATION.md) and [current runbook](../DEMO.md).
No controlled concurrency-one/two live benchmark or verified image fix is claimed.
Earlier pending/unpublished statements below are historical.

Local core.py now bounds incident calls with an asyncio semaphore (default two,
explicit concurrency=1 for baseline), preserving packet order, validation, partial
status, timeout per active call and zero retries. Queued time is not part of the
95s call budget. Cancellation cancels/joins sibling tasks and re-raises.
Incident elapsed/stage diagnostics and sanitized logs added; no prompt/model change.

15 CLI tests ran: 14 passed, one SDK-only skipped. The new controlled async test
checks concurrency one/two peaks, ordering, independent failures and secret exclusion.
builder_check ready=true; local Semgrep scan unavailable/unknown.

Not published or live-benchmarked. Exact-version AMS response confirms 0.1.1 is an
automated ams-base-rebuilder rebuild of 0.1.0, retaining source bundle
5dc58c91-5065-4cea-aa11-0252cb621e40. It was created at 19:00:41.017050Z, overlapping
the failed parent/child execution window. No operator source change is indicated;
causality remains unproved. Next implementation version is 0.1.2, not 0.1.1.
Still needs real SDK tests and controlled live
concurrency one-versus-two timing/completion comparison; no speedup claimed.

Update: managed SDK verification passed all 15 tests without skips. Published
0.1.2, source bundle 25236cc9-0f35-4ddf-94f9-5f765f1f434e, active/latest.
Integrated acceptance parent inv_5cd183b6-4312-4858-aad3-489da7fe4d1a running at
checkpoint. No controlled live speedup claim yet. Prompt/model unchanged.

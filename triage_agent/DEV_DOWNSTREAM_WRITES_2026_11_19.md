# Dev downstream managed-write verification — 2026-11-19 UTC

Operator explicitly authorized downstream verification. Verified active profile
`scalegov-dev`, tenant `69dfa4b844ff488d98b2674f`; Enrichment **0.1.6** and
Recommendations **0.1.10** active/latest. No staging requests or source/config
changes. These are direct receiver file-mode tests, not a repaired automatic
structured chain, and not browser/UI download acceptance.

## Enrichment — confirmed 2/2 exports

Exactly one published Harness dispatch with a single sources/file reference to
confirmed Triage file `0eb654aa-37a1-4861-97be-80b056d48b4e`.

- Invocation `inv_9f6ed465-2f53-4865-9197-cf034fd8c9bf`.
- Thread `de431fb2-1427-428b-8cea-0964deb0e54e`.
- Platform completed; application partial because AWS history is unconfigured:
  23 prepared criteria, all not_configured, no live historical searches.
- Code-owned receipt matches original file ID and exact-byte SHA-256
  `1e8a205afaa99b7c59f059518a73e1dad75fc840f852619969ba1cf0d1829121`.
- Original v3 canonical SHA-256:
  `cf4081b27bca2a47fe86c7aaecc6a646a4082c6952ac46ab3e60b0036efca9d8`.
- Full structured enrichment payload SHA-256:
  `4273aad482d624b550295138a0f6b0bcf30ce46003823f00edc6ad519b74ab18`.
- `export_status=completed`, `export_diagnostics=[]`. Both exports have
  status=created and matching file blocks in the run_enrichment OutcomeEvent.

| Filename | Confirmed ID | SGP size | Metadata created_at | Metadata MD5 |
|---|---|---|---|---|
| enrichment_results.json | `ffae5988-e50d-4485-9a02-67e99f5d5dc2` | 22,525 | 2026-11-19T18:45:58.697000 | `aec8fc5f749a90f6e474242963c6503d` |
| enrichment_report.md | `97a4f67c-3b10-47db-9e7b-ea63504ad9ff` | 6,627 | 2026-11-19T18:45:58.917000 | `db5883639cdc2cd6a491edbdd71ab3a6` |

Both metadata GETs returned HTTP 200. Markdown content GET returned HTTP 200 and
correctly discloses partial/not_configured history. Success diagnostics do not
retain upload HTTP status; no numerical upload status is claimed.

## Recommendations — confirmed 2/2 exports

Exactly one published Harness dispatch with a single sources/file reference to
confirmed Enrichment JSON `ffae5988-e50d-4485-9a02-67e99f5d5dc2`.

- Invocation `inv_2afaba8b-0750-4240-b0ba-e97a2380ac63`.
- Thread `afa461a9-d315-4ced-9523-f6f0b22d244d`.
- Initial observation running after 45 seconds. Read-only status/output reads
  only from this point; never re-invoke/resume to poll uncertain writes.

Final metadata confirms actual version **0.1.10**, platform completed; created
`2026-11-19T18:46:18.198402Z`, started `18:46:35.245233Z`, completed
`18:47:18.962048Z`. Output checkpoint `1f1e449a-5a9c-6ff7-8016-a0a2f6b4aedc`.
Code-owned run: partial, **1/1 analyses completed, zero failed**, upstream history
still unavailable and identity unresolved. `actions_executed=[]`, human review
required. This is not semantic certification of generated advice.

File receipt confirms exact Enrichment JSON file ID, exact-byte source SHA-256
`7c66345527a159175b544df1d5022fedce50337a77d5900d16517f2d9d048092`, and
canonical payload hash `4273aad482d624b550295138a0f6b0bcf30ce46003823f00edc6ad519b74ab18`,
matching Enrichment's structured result. Receipt establishes successful in-agent
read and validation of that export; no model reconstruction used for handoff.

Both exports status=created, export_status=completed, export_diagnostics=[], with
matching action-scoped run_recommendation file blocks:

| Filename | Confirmed ID | SGP size | Metadata created_at | Metadata MD5 |
|---|---|---|---|---|
| recommendation_results.json | `585696f3-e05a-4a36-8e2b-1db529faca3c` | 30,730 | 2026-11-19T18:47:18.361000 | `48ee925a5218a77a9b8ddd4c0b340e89` |
| recommendation_report.md | `06f51148-039f-4622-9dd2-906b09e89322` | 6,136 | 2026-11-19T18:47:18.572000 | `faf9482ce45eb30ac2577fa7a1a865e1` |

Both metadata and both content GETs returned HTTP 200. JSON schema is
alert-recommendations/1; source hash/partial status/synthetic flags preserved.
Decoded content readback is semantic verification, not an independent exact-byte
hash recomputation. Upload HTTP success codes are not retained by application
results and are not inferred from later GET status.

## Conclusion and limits

**All four downstream managed writes are confirmed**, with matching attachment
events and independently readable file metadata. Together with the earlier Triage
test, all five expected export types have now been created under SGP v8 in Dev.
Each receiver was invoked once; no submission or uncertain-write retries. No
platform or source changes, no response actions, staging unchanged.

These explicit operator-driven file-mode invocations do **not** repair or verify
the automatic structured chain. Triage's separate `structured_handoff_unavailable`
issue remains open. UI rendering/download and production storage are untested.

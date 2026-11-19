# Dev explicit SGP v8 release — 2026-11-19 UTC

Operator authorized using the existing `platform-sgp-runtime-http-v8` policy.
Verified active AMS profile `scalegov-dev`, tenant `69dfa4b844ff488d98b2674f`
before mutation. Staging was not called or changed. All IronVeil names retained.

Configuration-only release: reused the exact previously published source bundles,
unchanged models, dependency pins, extra routes and LiteLLM injection. Added
`external_access: ["platform-sgp-runtime-http-v8"]` through the MCPx publish API;
the typed builder_publish tool has no external_access argument. Each POST was
submitted once. No new source upload, hard-coded endpoint, environment override,
credential injection, custom policy, hotswap or platform-default change.

| Agent | ID | New version | Source bundle (unchanged) | Deployment |
|---|---|---|---|---|
| IronVeil Investigation — Start Here | `7f244b84-ff27-43b0-a629-99a76791373a` | 0.1.31 | `70f5149a-6bd9-4dd3-9aec-025823e448d6` | `76a41d7b-005a-4c45-b9a5-9ea2b0974a93` |
| IronVeil Historical Enrichment | `e8dc7ffc-c6d5-4920-9c12-a25e797835d8` | 0.1.6 | `ac7f2558-6581-408b-86e0-bf5f9fb1be55` | `f02bc430-4a45-47fc-912f-0415679ca250` |
| IronVeil Recommendations | `2cf86942-3a14-40e4-95e5-4a90e752b259` | 0.1.10 | `2b34dedb-4ea4-42a2-8fdd-4e4589581013` | `0b3e45d2-dec1-4fb0-97f2-d73bd2cc2262` |

All three exact-version reads confirmed the requested SGP policy and its pin:
revision **1**, digest
`sha256:e009dfc274fe4fa535f77bcc4b9a5935c8837f2d76dafd2653920c271c2c158f`.
All three config hashes:
`v1:sha256:780134705cbdb54358d6f7518a2da021b2d26721ad020eda72e409019e244c75`.
This proves API acceptance and policy pinning, not successful runtime storage.

Initial deployment state was pending/building_image for all three. Subsequent
`builder_status` reads confirmed **all three active/latest** on the verified Dev
profile and tenant. No new chain or file writes authorized by this change;
no invocation IDs or confirmed attachments claimed. A fresh synthetic acceptance
run requires separate approval; never retry earlier uncertain writes.

Prior source checks/tests and the failed synthetic chain are retained in
`DEV_DIAGNOSTIC_RELEASE_2026_11_18.md`; not rerun or overwritten here.

## Subsequently authorized write acceptance

One fresh test confirmed Triage file creation, matching attachment and HTTP 200
metadata/content readback. The chain then stopped before Enrichment submission
with `structured_handoff_unavailable`; downstream writes were not reached by that
chain. See [exact acceptance evidence](DEV_SGP_V8_ACCEPTANCE_2026_11_19.md).
Subsequently authorized direct file-mode receiver tests confirmed **all four
downstream exports**, matching file blocks and SGP metadata, with successful
Recommendation analysis (1/1); [receipts and file IDs](DEV_DOWNSTREAM_WRITES_2026_11_19.md).
No retries. The automatic handoff issue remains open; AWS history and production
storage remain untested/unconfigured as previously documented.

## Publication recheck and reproduction boundary

Before the documentation commit/push, fresh `builder_status` reads again confirmed
0.1.31 / 0.1.6 / 0.1.10 **active/latest**, same Dev tenant. No redundant publish
or new invocation was performed. Only managed-file access is fixed/verified;
these are not represented as fully fixed workflow agents.

The policy is a **publish-time** setting, not a graph or manifest setting. Future
releases must preserve `external_access: ["platform-sgp-runtime-http-v8"]` through
the MCPx API, together with the existing routes and LiteLLM injection. A default
builder_publish call cannot carry that argument and must not silently drop it.
Use the existing agent IDs and current IronVeil display names above; recheck
profile/tenant and policy availability before any separately authorized release.
No application source or dependency changes were required for the storage fix.

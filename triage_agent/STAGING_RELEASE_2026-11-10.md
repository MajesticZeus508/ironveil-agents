# Staging rebuild and polling-fix promotion — 2026-11-10

> **Current reading guide:** all three release versions remain active/latest at
> housekeeping recheck. The initial guarded-handoff failure and subsequent
> successful second test are both retained below. Later five-run evaluation:
> [28/35 successful analyses](STAGING_PERFORMANCE_2026-11-11.md). Pending wording
> is a chronological observation, not an instruction to submit another test.

Operator reported the staging base-image fix ready and explicitly requested
redeployment. Confirmed `scalegov-staging`, tenant
`6a1099f9e1ca37ee1216d8c3`; all three prior deployments were inactive.
No restore, security bypass, dependency pin changes, Dev deployment changes,
VoF migration, model fallback, inference timeout change or Git commit.

## Source and verification

- Enrichment `ams/` and Recommendation `ams/` rebuilt without source edits.
- Entry polling fix from Dev 0.1.25 prepared in isolated
  `releases/staging_0_1_24/`, leaving `plugins/alert_triage/` Dev-targeted.
  `tests/prepare_staging_release.py` copies 17 runtime/metadata files, verifies
  exact replacement counts, compiles Python, and writes per-file source/release
  SHA-256 provenance outside the pod at
  `releases/staging_0_1_24.provenance.json`.
- Only three receiver-ID occurrences differ from the Dev working pod: Enrichment
  in `handoff.py`, Recommendation in `handoff.py` and `stages.py`. Staging IDs:
  `420e63bd-8220-48bd-bada-743f0daea46c` and
  `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f`.
  Existing Dev-oriented source comments in the release copy are historical;
  the verified literal receiver IDs determine routing. No release-copy edits.
- Managed local verification: 60 Triage + 15 Recommendation tests passed with
  zero skips, then five-stage graph/checkpointer verification with five files.
  Enrichment ordinary CLI: 24 tests, 22 passed, two SDK skips; core freshness passed.
- All three `builder_check` results ready=true, no blockers. Semgrep unavailable:
  local deployment scan unknown. Strict Harness, exact receipts, extraction-only
  default, AWS unavailable and human-review/no-actions boundaries preserved.
- Existing SAK 0.50.0/scaffold pins and graph construction unchanged; this is an
  application promotion/rebuild, not an SDK migration.

## Publications

| Agent | Existing staging ID | New version | Source bundle |
|---|---|---|---|
| Entry | d4ffbfc9-696f-4a5a-b174-75daaa1c993f | 0.1.24 | b06c9ba3-3223-4bdb-8281-61fba2bab92e |
| Enrichment | 420e63bd-8220-48bd-bada-743f0daea46c | 0.1.3 | 2eb071f0-fe65-4d6f-a477-17819787f720 |
| Recommendation | 934ba6f7-3dcc-4dfb-9454-acdc92f7a10f | 0.1.4 | eb82adf2-8f84-4008-9da8-48bdbe6b929b |

Enrichment/Recommendation active/latest and hosted Harness negative acceptance:
- Enrichment `inv_5636a438-fbea-4f12-b375-9800d1b6c0b6`, thread
  `4e9e524f-9f70-4ae6-866f-a3aac60fb5d4`: completed, `missing_handoff`.
- Recommendation `inv_27d704d1-c4fd-451a-9546-391a5813c6ad`, thread
  `4412994e-f248-4770-ab1b-75a82174f0c2`: completed, `missing_enrichment`.

Deployment IDs: Enrichment `1dc3f2b4-209d-4001-b50c-d7e22b5ed134`;
Recommendation `5eba407b-b4e5-499a-a590-852065925632`.
Image digests returned:
- Enrichment `sha256:a1dec129b99f0c3bb0c1b861b8f963ae32b42b088d92d6db8f75af649a0067dc`
- Recommendation `sha256:3fed439b20be24287a08bffe8d59876e254782399e5b5c4ca5121999978c9587`

Both report compromised=false and takedown_at=null at this checkpoint.
Enrichment digest differs from previously flagged
`sha256:d14f490ea1555e76a100bf40e08ac235d3194e4da3e5928ab0406cf27111ef83`.
No fresh SBOM/package scan was supplied: neither active status nor a changed
digest independently attests libexpat1 remediation. Platform security ownership
and the operator's reported fix remain distinct from functional acceptance.

Entry activation/full-chain acceptance recorded below as available. Existing
synthetic staging upload `61827a37-3cb1-4a13-8445-cdf1e5ad8ded` is accessible:
run2 findings, 62,315 bytes, metadata MD5 `eb39e52b1f56da07285de643738c9949`.

## Final activation and acceptance checkpoint

All three target versions active/latest. Entry display name and Donovan/upload
metadata preserved (`ps:donovan:chat`, one required file, 1,000,000-byte limit).
Entry deployment `dce94c91-f4ec-40ea-9b91-fadd510c5280`, image
`sha256:b4f041d8e35d49e32deee8894756da1f7d0288d9b44bde87a90a0e14c598b8b4`,
compromised=false, takedown_at=null at inspection.

Full-chain test submitted once: `inv_5e622817-b9b3-4b7d-b830-248fb151f046`,
thread `49ebf88c-477d-4e5f-9fd4-4272200e9bcf`. Platform completed but
**application investigation incomplete**:
- Triage: 17 findings, seven groups, 98 observations, zero input errors,
  deterministic extraction only, 2.691s.
- Enrichment child `inv_e2f7ca58-0a9a-4fd0-94ab-64bbfa458315`, thread
  `6f95a3ec-63c6-4495-a0df-ee0da05aaa27`, completed with partial/AWS unavailable.
- Enrichment submit 6.085s; collect 4.241s, four GETs, zero retries/errors.
  Exact file/hash receipt verified and two action-scoped file exports projected.
- `submit_recommendation` returned `enrichment_json_unavailable_or_unverified`
  after 0.437s, platform_status=not_invoked. Recommendation was **not submitted**.
  The existing guard covers byte-read status/type, parse/schema and receipt
  checks; it does not preserve which failed. Root cause is **not established**.
- Confirmed preserved files: Triage `520f6ada-51cf-4310-b843-a6a4300c9caf`,
  Enrichment JSON `ebdd190e-d716-41c1-8d04-b5a8d7881000`, Markdown
  `2f955d05-89e0-4410-8753-15ce7e24e563`.
  Independent operator-side JSON metadata GET succeeded (268,331 bytes); this
  does not prove the in-pod read or receipt guard succeeded.
- Stored top-level output exactly messages/render_events, durable paired stage
  events, three confirmed attachments, final explicit INVESTIGATION INCOMPLETE.

No validation weakening, file-read/write retry, replacement child submission,
automatic rerun or unrelated code fix was introduced to force acceptance.
Deployment restoration succeeded; five-file/full-chain acceptance **did not**.
Investigate the guarded Enrichment-to-Recommendation managed-byte-read/receipt
path separately before claiming staging demo readiness. Inference performance
and the libexpat1 scan attestation remain separate issues.

## Operator-requested second test

One fresh invocation, same synthetic staging upload and unchanged configuration:
`inv_cbd08334-b349-435f-8ca1-789b23c55660`, thread
`dd7e853a-addb-446e-9ec0-777a7d661a25`, entry 0.1.24.
Created `2026-11-10T23:26:25.037960Z`, started `23:26:30.699118Z`.
Unlike the first acceptance, this run passed the guarded handoff and submitted
Recommendation 0.1.4: `inv_ba2c8125-1521-4e0b-baa7-fe87484e30ff`, thread
`62e346b3-d87f-45bc-b2d6-cba50f4f4602`, started `23:26:50.342796Z`,
input Enrichment JSON `d890348d-6bb4-46ba-b1df-ecbe62f16b2b`.
Parent and Recommendation still running at this check; final acceptance pending.
Follow-up observations were read-only GETs, no resubmission. Passing the handoff
on this run does not establish the first run's failure cause or a permanent fix.

### Second test terminal result

Read-only follow-up confirms parent completed `2026-11-10T23:28:48.924293Z`:
**143.886s creation-to-completion**, 138.225s after start. All five stages and
five action-scoped file attachments confirmed; **7/7 recommendations, zero failures**.
Recommendation completed `23:28:46.948323Z`: 116.606s active execution,
122.021s creation-to-completion. Parent finished 1.976s after the child.

Stage durations: Triage 1.903s; Enrichment submission 6.065s / collection 4.205s;
Recommendation submission 6.851s / collection 117.404s. Enrichment collection
four GETs and Recommendation collection 58 GETs, **zero retries or polling errors**.
Both child submission counts one. Receipts and strict messages/render_events
output confirmed; application remains partial because history is unavailable and
upstream narrative deferred, not because Recommendation failed. Human review
required, no actions executed.

Files: Triage `6fe76b77-a75b-4f6b-92e7-e64d7f56f467`; Enrichment JSON
`d890348d-6bb4-46ba-b1df-ecbe62f16b2b` / Markdown
`43cdd648-bcff-4a7b-896d-88aa6a74131f`; Recommendation JSON
`50cbefdb-3b80-4898-89e0-59f01497e522` / Markdown
`8a9b389b-6b61-48a4-8a40-0358400547ca`.

Enrichment child `inv_9cb34005-4801-49a6-abb7-3ccf499dd9f8`, thread
`12fc3cd8-a1a7-4932-a9ac-9bd4290c4f34`. Recommendation input SHA-256
`c35ae4e81a2857f78dccc68fa937b03777d7d11c215bf472db3c0a426c5b19df`.
This establishes one successful hosted chain after the earlier guarded failure;
it is not a reliability SLA, security attestation or diagnosis of that failure.

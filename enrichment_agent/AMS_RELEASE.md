# Historical Enrichment POC — AMS release

**New rebuild:** 0.1.3 is active/latest after the operator-reported staging fix;
hosted missing-handoff check passed. Source unchanged. See
[release evidence](../triage_agent/STAGING_RELEASE_2026-11-10.md).
The older security checkpoint below is historical; fresh scan/SBOM proof is still
not supplied by functional activation alone.

> **Historical security checkpoint, before 0.1.3.** Both 0.1.0 and the
> unchanged-source rebuild 0.1.1 were taken down for vulnerable `libexpat1`.
> Operator-requested 0.1.2 was active/latest but had the same reported image digest
> as 0.1.1, not a verified fix. See retry evidence below and
> [image investigation](IMAGE_SECURITY_2026-11-10.md).

Environment: ScaleGov staging; tenant `platform`
(`6a1099f9e1ca37ee1216d8c3`).

- Agent ID: `420e63bd-8220-48bd-bada-743f0daea46c`
- Version: `0.1.0`, published (not a draft).
- Source bundle file ID: `957c7e7c-af75-4b38-bc6f-dafc077fc983`.
- Publish accepted 2026-11-07; version subsequently verified **active and latest**.
- Pre-publish: 24 tests ran, 22 passed and two SDK tests skipped. Core staging
  verified. Packaging ready=true; local Semgrep unavailable.
- AWS remains not configured; automated Triage → Enrichment invocation is not
  implemented. Triage source and deployment were not changed.

## Hosted acceptance evidence

### Historical operator full-chain acceptance — 2026-11-10

After the isolated provisioning failure below, operator parent
`inv_b394de1e-5e49-4616-8495-f936041f9844` successfully invoked Enrichment **0.1.2**:
child `inv_6ad508d1-fc73-43d5-a681-6ed42b46d45e`, thread
`46dfb5be-e490-4d53-bcca-1eae05169a74`. Created `02:09:14.226165Z`, started
`02:09:19.581598Z`, completed `02:09:22.535941Z` (8.310s including startup).
Input `969c7c66-13b9-4dbb-a4c2-1e5196651eaa`, SHA-256
`b4676c83c971852ef74318f122b2077014a249c840579781682ab758dda24c63`.
Both outputs confirmed in the parent: JSON `495a9a58-e68a-4cbf-87e1-46700e12f212`,
Markdown `45968bb7-db1d-49ca-b719-bed76b8b26af`. AWS `not_configured` and
application partial retained; Recommendation then completed 7/7 analyses.
Operator confirmed Donovan success; [full-chain evidence](../DEMO.md).
This functional success does not prove the same-digest image was patched.

### Operator-requested rebuild retry — 2026-11-10

The operator explicitly requested another AMS build after observing automatic
replacements of Triage and Recommendation. Published unchanged retained source
`957c7e7c-af75-4b38-bc6f-dafc077fc983` as **0.1.2** using the current platform
default base (no base pin, security exception or restore).
Deployment: `5b3a1e78-ca67-40ad-a123-3b687e36a8a2`.
Publish accepted; initial state pending. A new build is not evidence that the
OS package is patched; final image scan/package evidence remains required.

Subsequently verified active/latest, deployed `2026-11-10T02:06:04.844871Z`,
with `compromised=false` and no takedown deadline at that check. **The reported
image digest is identical to vulnerable 0.1.1:**
`sha256:d14f490ea1555e76a100bf40e08ac235d3194e4da3e5928ab0406cf27111ef83`.
This is not a patched image or a clean-scan attestation. Security checks were
not bypassed. Functional test `inv_d27f0492-239f-41b7-a52e-511e0d50d81e`,
thread `af2a1b1e-5d61-4296-a53b-26e44cc88e03`, uses the previously verified
handoff `9b7d4c41-52ca-45ce-85fc-51d7d0440189`; initial observation remained
`deploying_sandbox`, with no reply yet.

The test then failed before graph execution at `2026-11-10T02:07:14.495351Z`:
`SESSION_PROVISIONING_FAILED`, admission/pre_graph, retryable=true. Runtime
provisioning received HTTP 503, `Authorization service unavailable`, while
listing sandbox resources. No application reply was produced. This is a separate
platform provisioning failure, not evidence about the XML library or input.

### Original 0.1.0 acceptance

The first test used `61827a37-3cb1-4a13-8445-cdf1e5ad8ded`, which is the original
findings upload, not the handoff. The receiver correctly rejected it as an invalid
handoff. Do not confuse the handoff's nested `source.input_file_id` with the ID
of the handoff file itself.

The matching v3 handoff is `9b7d4c41-52ca-45ce-85fc-51d7d0440189`:
its file metadata MD5 matches local `extracted_indicators (3).json`
(`44683aaca423ad914be3088beb7bce30`). The receiver read and validated it.

- Successful invocation: `inv_b560396a-070a-493b-85e3-3cd72abf73fc`.
- Thread: `bd68a506-15b8-4771-9947-2a6fd71eac76`.
- Received SHA-256: `93ce4f8179aacb55aa6cb28d81f18b8264e5dd6d657bd6e11c6e24edc6d29585`.
- 323 planned queries; all 323 explicitly `not_configured`; application run
  `partial`, platform invocation completed. No historical searches ran.
- JSON export: `ddd9fc6f-05e2-444f-8f2e-72d97374bff7`.
- Markdown export: `9b513702-8ee6-4fb4-b5ac-cd3897b1700a`.
- Stored output top-level channels: `messages`, `render_events`; confirmed tool
  outcome included both file blocks. No top-level working state or task channel.
- Same-thread Harness text-only follow-up
  `inv_513d51b8-d2e3-43bc-8620-9f7f96429cb2` returned `missing_handoff`; it did
  not reuse the previous attachment. A messages-style follow-up was rejected at
  the input boundary; use explicit Harness input, not inferred message shapes.

No direct downstream Donovan discovery tag is needed; the entry projects verified
files. Original direct-receiver UI verification was not claimed.

## Current evaluation and preservation

Live recheck confirms **0.1.3 active/latest**, source
`2eb071f0-fe65-4d6f-a477-17819787f720` (file metadata GET 200).
Latest five hosted chains exercised 0.1.3 with both exports and `not_configured`
history retained. Fresh CLI: 24 discovered, 22 passed, two skipped; freshness passed.
See [evaluation](../EVALUATION.md) and [source-backup gaps](../AMS_INVENTORY.md).
Older “no automated invocation” and “latest” statements above describe 0.1.0 only.

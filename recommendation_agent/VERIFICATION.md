# Recommendation Agent verification — 2026-11-09

**Staging rebuild 2026-11-10:** unchanged source published as 0.1.4, active/latest;
hosted missing-enrichment check passed. See
[release evidence](../triage_agent/STAGING_RELEASE_2026-11-10.md).
This is not an inference-performance fix or independent image-security attestation.

## Current housekeeping result

Live AMS **0.1.4 active/latest**, source `eb82adf2-8f84-4008-9da8-48bdbe6b929b`;
source-file metadata GET 200, no fresh downloaded byte comparison. Fresh ordinary
CLI: **15 discovered, 14 passed, one SDK skip**, no failures. Python 3.9.6 is below
the documented 3.11+ floor; no new managed/live-model test was run.
Latest five-chain evaluation: **28/35 successful analyses**, six timeouts and one
validation rejection. Both exports confirmed in all five chains. See
[team summary](../EVALUATION.md), [performance](PERFORMANCE_2026-11-11.md) and
[backup gaps](../AMS_INVENTORY.md). Older latest/integration claims below are historical.

## Historical checkpoint — 2026-11-10 UTC, before 0.1.4

**0.1.3 active/latest**, automatic `ams-base-rebuilder` replacement of 0.1.2,
source bundle `25236cc9-0f35-4ddf-94f9-5f765f1f434e`. Concurrency-two
implementation released in 0.1.2; prompt/model and schemas unchanged. Prior
managed regression passed all **15 Recommendation tests**, no skips.

Operator-confirmed Donovan full-chain parent
`inv_b394de1e-5e49-4616-8495-f936041f9844` completed with five files in 206.181s.
Recommendation child `inv_7eb8f911-ed1f-47cb-97ae-351aa42eef06`, thread
`6c85e3ea-47a3-491f-9617-e124413ef245`, version 0.1.3: created
`2026-11-10T02:09:36.197183Z`, started `02:09:42.443376Z`, completed
`02:12:30.651571Z` (174.454s including startup, 168.208s after start).
7/7 analyses, zero failures, application partial (upstream limitations retained).
JSON `25fed65e-942d-48f7-be85-a351e3cf43b4`; report
`9ccc6a9b-1ae1-48a6-a180-82ea522a5e6c`. Parent confirms exact input receipt and
both action-scoped output file blocks. Full hosted narrative audit not claimed.

No direct downstream Donovan discovery tag is needed: entry projects the files.
Controlled live concurrency-one/two comparison remains unperformed; no causal
speedup or SLA claim. Image-security remediation is separate from functional
acceptance; see [shared runbook](../DEMO.md). Earlier 0.1.0 and deferred-integration
statements below are historical checkpoints, superseded where noted above.

## Built

Separate `ams/` pod scaffolded with Argon `gemini/gemini-4-argon` from the live
ScaleGov model catalog. Its streaming/system/tool-schema gateway check passed.
Triage, Enrichment, their snapshots and deployed versions were not changed.
No agent-to-agent automation, AWS access or response execution was added.

Reviewed shared project documentation; all top-level documentation in both agent
directories; Enrichment's hosted README, core, receiver, routing and input contract;
Triage's extraction/grouping, model validator, export and provider compatibility;
actual complete/pending enrichment examples and the compatibility tests.
The broader original Enrichment design is superseded by historical search.
No v4 producer migration or external intelligence source was assumed approved.

## SDK verification

Checked ModelConfig, CompletionAgent, Harness resource input, SGP raw-byte reads /
additive writes, and ToolLifecycle against Agent Kit **v0.50.0** source and its
exact-version documentation. Checked billing, coding middleware and prompt-cache
behavior at sling-agent-v0.1.0.dev6. Scaffold-owned requirement pins preserved.
The bundled source snapshot is 17 days old and may lag upstream; an operator can
refresh it with `sling sources update` (or `--from FILE` in a closed environment).

## Repeatable tests

- Plain CLI: 14 tests; 13 pass, one SDK-only check skipped.
- Managed runtime: all **14 tests pass**, no skips.
- Seven-incident / 98-observation existing Enrichment export parses successfully.
- Tests cover schema/joins/counts, null/zero/provenance, unavailable history and
  upstream context, uncovered negatives, malformed JSON, invented targets/refs/IPs/
  domains, ungated containment, prose ratios/clocks, sanitized failures, exact
  managed reads, missing attachments, write uncertainty and escaped Markdown.
- Input/output validation is not complete semantic fact-checking or a live
  adversarial prompt-injection certification.

## Real local Argon calls

The standard `builder_probe` imports the production graph but submits legacy
messages input. Its rejection occurs before inference because production requires
the closed Harness task/resource-file contract. That contract was not weakened.

The local-only `tests/live_probe/` runner imports the actual production source:

- All tests pass with the real SDK.
- Invokes the actual production graph with a Harness text-only task: returns
  `missing_enrichment`, public channels exactly `messages` and `render_events`,
  paired tool events, no invented attachment or provider call for routing.
- Runs actual Argon analysis on one complete synthetic-history example and one
  AWS-pending example. Final schema-bound run: **2 calls, 2 validated analyses,
  zero gateway refusals**. Complete case completed; pending case remains partial
  despite a completed narrative. Zero actions executed.

Final saved examples (before the subsequent code-owned report decision gate and
additional upstream metadata preservation; model prompt/client unchanged):

- `outputs/live_2026-11-09T15-42-09.454449+00-00_verified_demo/`
- `outputs/live_2026-11-09T15-42-32.172014+00-00_aws_pending/`

Earlier experiments included validation rejections with evidence retained and
no fabricated narrative. Provider JSON schema constraints were added rather than
loosening local length/reference checks. Historical examples remain synthetic;
these runs do not prove live AWS or hosted managed-file integration.

Manual prose review found useful expert hypotheses but also occasional overly
quick closure suggestions and inferred connection details. The prompt explicitly
forbids these shortcuts; a deterministic report-wide decision gate additionally
requires corroborated authorization/scope and no conflicting evidence before
closure or de-escalation. This is a remaining model-quality risk requiring analyst
review, not a claim that prompts or structural validation eliminate hallucinations.

## Package and release

`builder_check`: **ready=true**, no packaging blockers. **Security verdict unknown**:
Semgrep is not installed, so no local deployment scan ran. The catalog/model was
verified separately. The pinned package's availability in the target deployment
index was not established by the local tests alone. The subsequent successful
deployment and hosted invocation provide evidence that this release installed
and started in staging; they do not supply a local security-scan attestation.

AMS publication of **Recommendation Agent POC 0.1.0** was accepted in ScaleGov
staging, tenant `platform` (`6a1099f9e1ca37ee1216d8c3`), on 2026-11-09.
Agent ID: `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f`.
Source bundle file: `5dc58c91-5065-4cea-aa11-0252cb621e40`.
Version **0.1.0 is active and latest**. Deployed Harness missing-file smoke
completed successfully: invocation `inv_d1215975-3506-435e-8039-20391c0d75a5`,
thread `7637849b-4ce0-4e5f-9c13-9a317a584cb2`; returned `missing_enrichment`
with no stale upload or invented output.

Hosted full-handoff acceptance completed using the existing Enrichment export
`ddd9fc6f-05e2-444f-8f2e-72d97374bff7` (the documented AWS-pending output).
Invocation `inv_17cdd190-3eff-46ee-a09f-311e832a7e6c`, thread
`2d9e2a64-8f54-4e8b-8ca7-4e78d1532727`; terminal platform status `completed`.

- Created: `2026-11-09T15:45:42.515529Z`; started `15:45:48.823899Z`;
  completed `15:49:19.798167Z`. Submission-to-completion **217.28s**;
  execution after start **210.97s**. One run, not a benchmark distribution or SLA.
- Application status `partial`; **seven completed analyses, zero failed**.
  The original Enrichment export is AWS-pending, so partial status is expected.
- Received SHA-256:
  `238e8529b1dc38feffa315bb56a1d811156a5acd9343bd2673454fdf87d1f1f3`.
- Confirmed JSON file: `52324851-2efd-4ef5-8a55-26fc87f5755b`.
- Confirmed Markdown file: `1b6a9096-a781-4a1f-ae0d-a7a287a2da05`.
- Stored output top-level channels are exactly `messages` and `render_events`.
  Successful `run_recommendation` outcome includes both durable file blocks and
  final AI status. `report=null` in tool status means the report exceeded the
  inline-chat threshold, not that file generation failed.
- Evidence checked through existing invocation/output APIs; no extra inference
  run was launched for housekeeping. File creation was confirmed by the successful
  tool result and file events; full hosted file contents were not independently
  downloaded/audited during this pass.
- The operator subsequently confirmed the AMS **Invoke** workflow works. Their
  separate invocation ID was not supplied; do not assign the builder's ID to it.

No Donovan-discovery metadata has been created. Donovan listing/rendering,
automatic agent-to-agent handoff, and live AWS coverage remain unverified/deferred.
Source checks are not evidence of hosted success. Only `ams/` was published,
not the diagnostic pod or surrounding outputs/tests.

## Housekeeping checkpoint

On 2026-11-09, rechecked **0.1.0 active/latest**, inspected the completed hosted
invocation and stored output, and reran the plain CLI suite: **14 ran, 13 passed,
one SDK-only check skipped**. The earlier all-14 managed result remains separately
labeled; no fresh managed/live-model test was necessary for documentation changes.

Updated operating instructions, contract, maintenance boundaries, output index and
shared workspace navigation. Preserved all experimental outputs, diagnostic source
and production application source unchanged. No new release, metadata mutation,
Git commit, AWS access or upstream-agent edit was performed. No downloaded source
snapshot/byte-for-byte published-bundle comparison is claimed for this agent.

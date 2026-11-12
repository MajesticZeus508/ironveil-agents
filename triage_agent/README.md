# Alert Triage Agent — proof of concept

**Demo update:** see [DEMO.md](../DEMO.md) for the three-stage entry application,
current release/acceptance checkpoint and Donovan run instructions. It supersedes
older standalone/two-stage operating instructions below where they conflict.

This agent now lives in `agents/triage_agent/`. Run all commands below from this
directory; paths in this document are relative to it. The move changed only local
organization, not the published AMS agent or application source.

An investigation aid for synthetic UEBA network findings. Python extracts and
validates facts; Gemini Argon supplies bounded hypotheses and human next checks.
The agent does **not** establish compromise or take response actions.

## Current release

**Staging rebuild/promotion:** see [2026-11-10 release evidence](STAGING_RELEASE_2026-11-10.md)
for entry 0.1.24 and downstream rebuilds after the operator-reported base-image fix.

**Dev follow-up:** [DEV_RELEASE.md](DEV_RELEASE.md) records the separate Dev
deployment; [bounded polling retries](POLLING_RETRIES_2026-11-10.md) records the
entry-only 0.1.25 change, tests and hosted verification. The staging checkpoint
below remains historical and was not modified by this Dev release.

**Live AMS recheck:** Triage **0.1.24** is active/latest in staging,
source bundle `b06c9ba3-3223-4bdb-8281-61fba2bab92e`.
Local staging source is `releases/staging_0_1_24/`; editable
`plugins/alert_triage/` targets **Dev**, not staging. The entry orchestrates Enrichment then
Recommendation through five checkpoint-sized stages. Triage inference is disabled
by default; narrative is deferred to Recommendation. Latest operator-confirmed
full-chain run on older 0.1.23 returned five files and 7/7 recommendations in **206.181s**.
The newer five-run evaluation returned **28/35 successful analyses**, six timeouts
and one validation rejection; median end-to-end **190.490s**. See
[team evaluation](../EVALUATION.md); do not substitute the old success for current reliability evidence.
See [current runbook and exact evidence](../DEMO.md) and
[reliability implementation](RELIABILITY_WORK.md).

| Item | Current value |
|---|---|
| Display name | Network Investigation Demo |
| AMS agent ID | `d4ffbfc9-696f-4a5a-b174-75daaa1c993f` |
| Environment | ScaleGov staging |
| Tenant | `6a1099f9e1ca37ee1216d8c3` (`platform`) |
| Latest published version | **0.1.24**, active/latest at live recheck |
| Configured model | `gemini/gemini-4-argon`; no Triage provider calls in default extraction-only mode |
| Handoff schema | `alert-indicators/3` |
| Tests | Fresh CLI: **44 passed, 16 skipped** of 60; prior managed: 60 passed |

Historical AMS 0.1.17 references the same source bundle used for 0.1.16. Its 14 restored
source/metadata files matched `plugins/alert_triage/` byte-for-byte at that checkpoint. The reason for
the intervening publication is not established by the available session record.
See [LOCAL_BACKUP.md](LOCAL_BACKUP.md). No new release was published for this
documentation cleanup.

## Use in Donovan

1. Open Donovan staging in the tenant above; refresh the agent list.
2. Start a new chat with **Network Investigation Demo**.
3. Attach **one UTF-8 findings file**, at most **1,000,000 bytes / 100 records**.
4. Ask: **“Run the network investigation and produce analyst recommendations.”**

Accepted content: JSON Lines, a JSON array, one finding object, or
`{"findings": [...]}`. Each finding must use `swoop-ueba-finding/1` and a supported
detector/measure pair. If the file picker rejects `.jsonl`, use a `.json` copy;
the parser still accepts JSONL content. The supplied local fixture already uses
that extension. The preserved local input is now `staging_input_verification.json`;
its 62,315 bytes and SHA-256 match the original run2 fixture. The old filename is absent.

The agent shows concise execution updates in Donovan's Thinking presentation,
then returns **extracted_indicators.json**, Enrichment JSON/Markdown, Recommendation
JSON/Markdown and a short count/error status when all stages complete.
The operator confirmed the revised presentation works. Updates are application
status, **not private model reasoning**. No sample dataset is bundled in the
deployed agent; missing/inaccessible uploads never fall back to old attachments.

## What happens during a run

1. Read only the current invocation's attached file ID through managed file access.
2. Validate records, preserve provenance, and record unsupported/malformed input.
3. Collapse identical finding IDs; quarantine conflicting contents under one ID.
4. Group by entity type/id/site, incident key, and UTC start/end window.
5. Extract IP/domain inventories and exact evidence observations deterministically.
6. Default to extraction only, marking narrative `narrative_deferred`, with zero
   Triage model calls. Create a managed JSON file only on confirmed write.
7. Submit/collect Enrichment, verify its exact file/hash receipt and exports, then
   submit/collect Recommendation and project verified attachments. Stage failures
   preserve prior outputs and are explicitly incomplete.

Hosted routing and final status are code-generated; they add no outer provider
calls. For the supplied fixture, this means **17 findings → seven incident groups
→ zero Triage model calls → 98 deduplicated evidence observations**. Recommendation
makes seven incident calls with concurrency bounded to two. Observations are
not 98 distinct malicious indicators or independent corroborations.

## Facts, context, and output

Python owns identifiers, provenance, indicators, supplied enrichment, detector
metrics, sample statistics, review priority, and `needs_review` disposition.
Highest supplied supported severity sets priority; it is not a maliciousness score.

Optional live Triage context (`TRIAGE_EXTRACTION_ONLY=false`) is limited to one or two explicitly labeled hypotheses and
exactly two defensive checks per group, each string at most 300 characters.
Provider JSON-schema constraints supplement local validation. The optimized hosted
path does not generate a separate summary paragraph; its summary field is empty.

The compact file contains:

- `source`: input file/hash/format and source-location semantics;
- `extraction`: counts, errors, and extraction status;
- `incidents`: entity/window, priority, disposition, context status/errors,
  validated hypotheses/checks and limitations;
- `indicators`: observation rows linked to incident IDs, containing `src`, `dst`,
  `protocol`, `bytes_sent`, `bytes_received`, `country`, `company`, `src_site`,
  and compact references. Time window is inherited from the incident unless overridden.
- `context_provenance`: model and interpretation warnings.

Company/country are supplied **unverified destination labels**, not WHOIS or
geolocation verification. The main fixture has no domains. Full local triage
results contain IP/domain inventories; the hosted handoff is observation-oriented,
not a complete per-IP/domain enrichment inventory. IDs are reproducible for the
same source/provenance, not cross-file entity identities.

**Read context status as well as extraction status.** Successful extraction/export
does not mean all model analyses passed. A platform-completed invocation can have
an application-level `partial` run. Failed context is explicit and never replaced
by invented narrative. See [INDICATOR_CONTRACT.md](INDICATOR_CONTRACT.md).

## Local files and development

| Path | Purpose |
|---|---|
| `plugins/alert_triage/` | Editable **Dev-targeted** application source |
| `releases/staging_0_1_24/` | Preserved staging release; do not edit |
| `ams_snapshots/0.1.17/alert_triage/` | Restored published source, kept separate |
| `triage.py` | Local CLI entry point |
| `tests/` | Deterministic, stub, export and real-contract checks |
| `staging_input_verification.json` | Hash-verified original synthetic run2 bytes; JSONL content |
| `outputs/` | Local example reports and saved verification evidence; inspect provenance |
| `plugins/triage_isolation/` | Local diagnostic pod, not the production agent |

### Repeatable offline example

The deterministic CLI/stub path uses Python's standard library. Run from this
directory with Python 3.11+:

```sh
python triage.py --input staging_input_verification.json --output-dir outputs/my_stub_run --stub --audit-export
python -m unittest discover -s tests -v
```

Use a fresh output directory, preserving historical examples. Pass `--input` explicitly:
the historical CLI default still names `.jsonl`. Stub output is labeled test data,
not a live-model result. Fresh ordinary CLI ran 60 tests: 44 passed, 16 skipped
for missing SDK/httpx. Python 3.9.6 is below the documented 3.11+ floor.
Prior managed regression passed all 60; not a fresh managed run in this pass.

CLI outputs are `triage_results.json`, `triage_report.md`, and compact
`extracted_indicators.json`; `--audit-export` additionally writes detailed v2
`extracted_indicators.audit.json`. Exit 0 means completed; 2 means partial/empty.

### Optional live CLI / hosted runtime

Use a separate SDK-compatible environment. The scaffold-owned pinned dependency
file is `plugins/alert_triage/requirements.txt`:

- `spark-agent-kit==0.50.0`
- `sling-agent==0.1.0.dev6`
- `ripgrep-bin==15.2.0`

Do not hand-edit these pins. Access to the package index carrying these releases
is required. The stdlib stub example does not require installing them.

A live CLI uses `LITELLM_PROXY_BASE_URL`, `LITELLM_PROXY_API_KEY` when required,
and optional `SPARK_MODEL_NAME` (default Argon). Obtain endpoint/access through
approved setup; never copy credentials from hosted settings into code or reports.
AMS injects runtime access. A local shell does not automatically inherit
Slingshot's managed gateway capability.

```sh
python triage.py --input staging_input_verification.json --output-dir outputs/my_live_run
```

Unlike the default hosted extraction-only path, the CLI uses full-narrative `LiveClient`.
Its output length/performance is not directly comparable to hosted benchmarks.
Agent Kit's `ModelConfig` is documented as “Connection settings and dispatch for
a LangChain-compatible chat model” ([0.50.0 reference](https://scaleapi.github.io/spark-agent-kit/reference/models/#spark_agent_kit.ModelConfig)).

## Performance and known limits

- Latest five-run staging sample: median **190.490s**, range 162.103–209.962s;
  **28/35 analyses succeeded**, one of five runs achieved 7/7. See [evaluation](../EVALUATION.md).
- Historical operator three-agent run: **206.181s** for 17 findings/seven incidents, 7/7
  recommendations; 12.13s/finding as a batch average, not individual latency.
- Historical standalone hosted runs: **103.34s** and **115.23s** for 17 findings.
- Historical thinking-presentation run: **287.65s**, with two 90-second
  context timeouts. Earlier full-output run: **385.14s**.
- Three overlapping 0.1.14 runs averaged **258.05s**; these are not isolated trials.
- In the older standalone path, seven sequential model calls dominated elapsed time. Startup/admission was about
  5–6 seconds in measured runs. The precise origin of inference delay—provider,
  serving queue, or gateway—has not been isolated. No latency SLA is claimed.

No live historical searches, DNS/WHOIS lookup, PCAP analysis, endpoint telemetry,
database or SIEM/SOAR actions are implemented. The new sequential handoff calls
the AWS-disabled Enrichment receiver; `not_configured` is not a search result.
Sample byte sums are not verified incident totals; direction is assumed relative
to `src`. Overlapping detectors are not additive. Null/zero-variance values remain
null rather than becoming zero. Validation is not complete semantic fact-checking
or a guarantee of prompt-injection resistance.

Managed exports create new files; uncertain writes are not retried automatically.
Classification/marking propagation remains unresolved. The requested base-image
`libexpat1` remediation requires platform ownership and has not been verified here.
Local Semgrep was unavailable: package `ready=true` is not a clean security scan.
No source changes or deployment were performed as part of this documentation pass.

## Handoff reading order

1. [SESSION_HISTORY.md](SESSION_HISTORY.md): chronological development, decisions,
   fixes, model changes, experiments, and unresolved work.
2. [DONOVAN.md](DONOVAN.md): current UI/API usage and failure interpretation.
3. [INDICATOR_CONTRACT.md](INDICATOR_CONTRACT.md): current handoff contract/migration.
4. [BENCHMARKS.md](BENCHMARKS.md): measurements and methodological limits.
5. [LOCAL_BACKUP.md](LOCAL_BACKUP.md): downloaded source and byte-match evidence.
6. [BUILD_STATUS.md](BUILD_STATUS.md): historical verification ledger, newest first.
7. [REVIEW.md](REVIEW.md): historical review and remaining cautions.

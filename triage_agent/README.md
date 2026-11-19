# IronVeil Investigation — entry point, orchestration, and triage

**Start here in Donovan:** select **IronVeil Investigation — Start Here**.
This directory implements the user-facing entry point for the entire workflow:
it performs triage, calls IronVeil Historical Enrichment, then calls IronVeil
Recommendations automatically. It is not only a standalone triage agent.

**Proof of concept:** approved synthetic data only; AWS history is unavailable,
human review is required, and no response actions are executed.

Former staging display name: **Network Investigation Demo**. The 2026-11-12
display-name/description update kept IDs, versions and source bundles unchanged.
The `triage_agent/` directory name and historical release records are retained.

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

**2026-11-18 checkpoint:** staging **Triage 0.1.30 / Enrichment 0.1.5 /
Reporting 0.1.9**, active/latest. Both structured handoffs and 1/1 incident
analysis completed. All three agents report `missing_sgp_configuration` with
request_may_have_been_sent=false: missing/blank sandbox SGP URL configuration
prevents upload dispatch. No attachments confirmed; INVESTIGATION INCOMPLETE.
Production untested. See [diagnostic release](DIAGNOSTIC_RELEASE_2026_11_18.md).

Current staging source is `releases/staging_0_1_30/`; editable
`plugins/alert_triage/` retains **Dev** receiver IDs. Do not publish it directly
to staging. Default extraction-only behavior, five stages and no automatic
submission/model/write retries remain. Full architecture and exact form/hash
contracts: [WORKFLOW.md](WORKFLOW.md). Reading order and historical release
distinctions: [DOCUMENTATION.md](DOCUMENTATION.md).

Recent history: LUX ingestion and bounded unknown/opaque-label compatibility
(0.1.25–0.1.27); serializer readiness rebuild (0.1.28); both structured handoffs
(0.1.29, successful authorized retry after ARP auth failure); safe-write diagnostics
(0.1.30). The dated release records preserve the intermediate failures rather
than describe today's state. [Structured release ledger](STRUCTURED_CHAIN_RELEASE_2026_11_17.md).

| Item | Current value |
|---|---|
| Display name | IronVeil Investigation — Start Here |
| AMS agent ID | `d4ffbfc9-696f-4a5a-b174-75daaa1c993f` |
| Environment | ScaleGov staging |
| Tenant | `6a1099f9e1ca37ee1216d8c3` (`platform`) |
| Latest published version | **0.1.30**, active/latest at 2026-11-18 checkpoint |
| Configured model | `gemini/gemini-4-argon`; no Triage provider calls in default extraction-only mode |
| Handoff schema | `alert-indicators/3` |
| Tests | Latest full SDK suite: **91 passed, zero skips**; joint total 151 |

Historical AMS 0.1.17 references the same source bundle used for 0.1.16. Its 14 restored
source/metadata files matched `plugins/alert_triage/` byte-for-byte at that checkpoint. The reason for
the intervening publication is not established by the available session record.
See [LOCAL_BACKUP.md](LOCAL_BACKUP.md). No new release was published for this
documentation cleanup.

## Use in Donovan

File uploads remain the normal Donovan entry. Explicit `lux_event` form ingestion
is also deployed for API/event callers; agent acceptance does not establish live
Events-rule configuration. See [current envelope](WORKFLOW.md#entry-input).

1. Open Donovan staging in the tenant above; refresh the agent list.
2. Start a new chat with **IronVeil Investigation — Start Here**.
3. Attach **one UTF-8 findings file**, at most **1,000,000 bytes / 100 records**.
4. Ask: **“Run the network investigation and produce analyst recommendations.”**

Accepted content: JSON Lines, a JSON array, one finding object, or
`{"findings": [...]}`. Each finding must use `swoop-ueba-finding/1` and a supported
detector/measure pair. If the file picker rejects `.jsonl`, use a `.json` copy;
the parser still accepts JSONL content. The supplied local fixture already uses
that extension. The preserved local input is now `staging_input_verification.json`;
its 62,315 bytes and SHA-256 match the original run2 fixture. The old filename is absent.

The agent shows concise execution updates in Donovan's Thinking presentation,
then returns a count/error status and only confirmed attachments. Intended files
are **extracted_indicators.json**, Enrichment JSON/Markdown and Recommendation
JSON/Markdown. Current staging storage is blocked, so five files are not promised.
The operator confirmed the revised presentation works. Updates are application
status, **not private model reasoning**. No sample dataset is bundled in the
deployed agent; missing/inaccessible uploads never fall back to old attachments.

## What happens during a run

1. Read the current explicit attached file, or validate the explicit LUX form object.
2. Validate records, preserve provenance, and record unsupported/malformed input.
3. Collapse identical finding IDs; quarantine conflicting contents under one ID.
4. Group by entity type/id/site, incident key, and UTC start/end window.
5. Extract IP/domain inventories and exact evidence observations deterministically.
6. Default to extraction only, marking narrative `narrative_deferred`, with zero
   Triage model calls. Create a managed JSON file only on confirmed write.
7. Submit/collect Enrichment through the structured v3 form; verify its canonical
   receipt and full structured result, then submit/collect Recommendation through
   the full-enrichment form. Intermediate write failure does not block analysis.
   Project only verified confirmed attachments; failures remain incomplete.

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
| `releases/staging_0_1_30/` | Current retained staging release; do not edit; older releases preserved |
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
not a live-model result. Latest full SDK regression passed **91/91**, zero skips,
Agent Kit 0.50.0. Older ordinary CLI skipped SDK/httpx tests and used Python 3.9.6,
below the documented 3.11+ floor. No full suite rerun for documentation cleanup.

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

- Latest diagnostic LUX chain: 1/1 analysis, both handoffs, no confirmed files;
  missing staging SGP configuration. Not a performance/reliability sample.
- Historical five-run staging sample: median **190.490s**, range 162.103–209.962s;
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

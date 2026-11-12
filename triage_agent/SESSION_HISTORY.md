# Alert Triage POC — session history and engineering handoff

## Current continuation guide

Staging entry **0.1.24**, Enrichment **0.1.3**, Recommendation **0.1.4** were
rechecked active/latest. Staging entry source is isolated under `releases/`;
editable plugin source targets Dev. Latest five-run evaluation achieved 28/35
analyses with five files in each chain; see [team evaluation](../EVALUATION.md).
Fresh CLI Triage: 44 passed, 16 skipped of 60 after test-only fixture-path repair.
Original bytes survive as `staging_input_verification.json`. Source backup gaps:
[AMS inventory](../AMS_INVENTORY.md). Historical evidence below is preserved.

## Historical continuation checkpoint — 2026-11-10 UTC

The original recount below ends at 0.1.17. Current entry is **Network Investigation
Demo 0.1.23**, automatic AMS rebuild of 0.1.22. Later approved work added automatic
Enrichment/Recommendation handoffs, then five checkpoint-sized stages, sanitized
diagnostics, default extraction-only Triage and concurrency-two Recommendation.
See RELIABILITY_WORK.md and [current runbook](../DEMO.md) for implementation and
complete acceptance evidence. Latest operator run completed in 206.181s, five
attachments, 7/7 recommendations. AWS remains disabled; image remediation remains
unverified. Historical “final/current” statements below describe that earlier session.

## Purpose and evidence standard

This recount consolidates the development session from the initial bounded brief
through the working Donovan demonstration and documentation cleanup. It is a
chronological engineering narrative, not a verbatim chat transcript. Evidence is
the local source/tests, historical BUILD_STATUS.md and REVIEW.md, BENCHMARKS.md,
saved progress verification, and AMS source/status checks. Unknown version actions
are identified rather than invented. Platform timestamps span November 5–6, 2026
UTC; no exact dates are inferred for unrecorded steps.

**Final state:** latest active AMS release 0.1.17; source identical to the local
thinking-presentation implementation developed as 0.1.16. Gemini Argon remains
the default. All 32 tests pass. The operator confirms Donovan is working well.

## 1. Initial goal and source review

The initial AGENTS/agents.md brief requested a local Python POC: parse synthetic
UEBA findings, extract indicators and supplied IP registration labels, explain
anomalies, recommend human review, and produce JSON plus a readable report.
It explicitly deferred integrations and autonomous response. Later requests
expanded the scope to AMS deployment, Donovan uploads, managed export and streaming.
The original brief remains a historical specification, not current deployment usage.

The supplied fixture has 17 `swoop-ueba-finding/1` findings across seven incident
groups, source `swoop/valhalla/simulated`. Entities include hosts, external service
and site. Detectors: fanout, protocol_mix, egress_volume, geo_spread, company_spread,
fan_in and site_volume. The file is now named `.json` but still contains JSON Lines.
Content hash: `6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a`.

Important constraints shaped the implementation: sample evidence overlaps and is
incomplete; one fanout detector reports 152 destinations but has only ten rows.
The combined four-detector group has 25 unique rows. Egress observations count
destinations uploading at least 100 MB, not bytes. Site zero-variance/null z-score
is legitimate. Company/country labels attach to destination IPs and are unverified.
Ports, DNS, endpoint activity, original PCAP, business intent and flow semantics
are absent; no compromise verdict can be justified.

## 2. Deterministic core and initial model-assisted triage

Python was made responsible for schema validation, UTC comparison, original
metadata/provenance, grouping, indicator extraction, enrichment association,
priority, exact-row deduplication and sample statistics. Identical finding IDs
collapse with all line references; conflicting same-ID contents are quarantined.
Malformed records generate explicit errors while valid ones continue.

IP/domain extraction preserves roles, paths and occurrences, keeps conflicting
labels, distinguishes missing/null/zero and avoids treating companies/sites as
domains. Separate edge fixtures exercise domains, malformed addresses and multiple
roles. IP classifications do not establish network ownership. Priority is highest
supplied supported severity; disposition starts at `needs_review`.

The model client was isolated in agent.py; code validates JSON structure, evidence
references and indicator mentions before accepting narrative. A stub supports
repeatable tests. Model failures retain deterministic output and sanitized errors.
Early probes exposed reference-catalog and lexical domain false positives; raw
schema paths such as `baseline.mean` were excluded from domain detection.

## 3. First AMS deployment: 0.1.0–0.1.2

The agent was packaged as a workspace pod using scaffold-owned pins:
spark-agent-kit 0.50.0, sling-agent 0.1.0.dev6 and ripgrep-bin 15.2.0. The graph is
module-level and retains billing/context scaffolding. Coding/file/network tools
are withheld; the bounded `run_triage` application tool supplies the workflow.

Initial deployed model was **openai/gpt-5.4**. Gateway shape checks and live local
fixture probes passed (17 findings/seven groups/seven contexts); the initial
hosted design used nine provider calls, including outer routing/final response.

- **0.1.0:** became active, but hosted import failed: AMS imports as a package while
  the local probe used a direct module import.
- **0.1.1:** fixed dual package/direct imports. Hosted fixture invocation completed
  17/7 with zero failures (`inv_73824d1b-0a39-4221-8279-1e78b8eb01ed`).
- **0.1.2:** added closed Harness task input, messages/render_events-only output,
  Donovan discovery metadata, malformed-input checks and durable lifecycle events.
  Hosted Harness fixture test passed (`inv_8b31a00d-c1ee-4bc2-96c8-c0da8fee99c9`).

At this stage the fixture/pasted-data workflow was historical behavior; it is no
longer supported in the deployed agent. Large tool output could be reduced by
outer context management, motivating a more explicit file handoff later.

## 4. Real uploads and exact observation handoff: 0.1.3–0.1.6

- **0.1.3:** removed bundled findings from deployment. Added one invocation-scoped
  managed file upload, 1 MB/100-record bounds and JSON array/object/wrapper support.
  JSONL retains physical lines; JSON containers label 1-based record indices.
  Missing/inaccessible attachments fail explicitly without fallback. Fake-reader
  tests and hosted denied-read/missing-upload tests verified the failure paths.
- **0.1.4:** added requested observation fields: time_window plus src, dst, protocol,
  sent/received bytes, country, company and source site. Every observation retains
  original evidence references and missing/null distinctions. Full local report
  renders this table. Test suite reached 15 checks.
- **0.1.5:** already existed in AMS when the next release was attempted; no distinct
  implementation history is established in these records.
- **0.1.6:** introduced `extracted_indicators.json` (`alert-indicators/1`), written
  to managed SGP storage and surfaced as a typed file attachment only on confirmed
  creation. Writes are additive, not overwrite-by-name; uncertain writes are not
  retried. Sixteen tests included fake-store success/denial and no invented IDs.

One early invocation hit platform 503 authorization unavailability before graph
execution. That did not prove an export defect. Upload picker support for `.jsonl`
was also limited in the inspected Donovan consumer; `.json` with JSONL content
became the practical workaround. Original source content was preserved.

## 5. Argon model change and compatibility repair: 0.1.7–0.1.9

The deployment switched from **openai/gpt-5.4** to **gemini/gemini-4-argon** in
0.1.7, using the platform LiteLLM endpoint through the OpenAI-compatible client.
No other successful deployed model transition is documented. Catalog candidates
and the model running this coding assistant are not the pod's configured model.

Although gateway shape preflight passed, the first complete hosted model request
failed. Diagnosis identified the optional scaffold PromptCacheMiddleware sending
`prompt_cache_key`, unsupported by Gemini's Vertex adapter (HTTP 400).

- **0.1.8:** omitted only that optional cache middleware for Gemini at graph
  construction. No dependency monkeypatch or credential change. Remaining
  middleware order/billing/context behavior retained. Hosted tool/final-response
  smoke and Argon context calls then succeeded; HTTP 400 resolved.
- **0.1.9:** introduced shared defensive SOC identity: calm, evidence-led, bounded
  investigation/handoff, no invented threat intelligence, attribution, enrichment
  or response actions. Eighteen tests passed and hosted persona smoke replied.

Local managed probe input became incompatible after the Harness contract change:
it imports the graph but submits legacy messages, rejected before inference.
Subsequent hosted Harness tests, not that probe, establish deployed behavior.

## 6. Context-bearing files and code review: 0.1.10

The handoff expanded to `alert-indicators/2`: one incident context entry per group,
linked from observations, with validated hypotheses, next checks, limitations,
model provenance, availability/errors. Failures leave context unavailable while
preserving extraction. IDs remain independent of narrative wording. Twenty-two
tests covered exact copying, linkage, duplicate keys, empty/partial data and errors.

A separate review (REVIEW.md) found useful unresolved concerns: row-oriented
handoff vs unique-IP enrichment, absent domain/ASN export, run/group issues repeated
on rows, source-dependent IDs, report size, lexical validation false positives,
stale docs and CLI filename, import-time assertions, dependency footprint and
tool denylist maintenance. Not all recommendations were adopted. In particular,
lexical indicator rejection remains fail-closed; no silent warning-only downgrade
or automatic JSON-fence repair was introduced.

The measured full-output 0.1.10 run took **385.14s**. Later optimizations should
not be read as controlled provider comparisons or proof of equal narrative quality.

## 7. File-first and reliability improvements: 0.1.11–0.1.12

**0.1.11** removed expensive outer provider calls: deterministic middleware
requests run_triage once and returns code-generated status. Hosted Markdown/full
chat report generation was dropped; the JSON file became the deliverable. Each
incident now requests only 1–2 short hypotheses and exactly two human defensive
checks, each ≤300 characters, using a compact payload. Fixed caveats remain
code-owned; no separate hosted summary is generated. Seven groups now require
seven sequential inference calls rather than nine, without concurrency/retries.

The first file-first benchmark took **275.39s**, about 29% below 385.14s, but
only three contexts passed and four failed. Seven ChatOpenAI spans totaled 267.83s;
outer deterministic passes totaled 3.88ms. This was not seven successful analyses.

**0.1.12** addressed reliability:

- Strict provider JSON schema constrains keys, array sizes and string length;
  local checks remain authoritative.
- Valid clock times are excluded from IPv6 candidate scans; full/compressed IPv6
  and invented/malformed address checks remain.
- Structured stage/type/code/field errors and call durations make failures visible.
- No retry, timeout increase, fallback model or unvalidated truncation was added.

One full 0.1.12 live run completed **115.23s**, all seven contexts passed and all
98 observations exported (`inv_8810bb70-a357-4757-a8dd-65774799f354`). Twenty-seven
tests passed at this stage. A success is not a guarantee against later timeouts.

## 8. Compact schema and latency investigation: 0.1.13–0.1.14

0.1.13 was already present remotely; the compact release used **0.1.14**. No
independent 0.1.13 behavior is attributed without evidence.

`alert-indicators/3` stores incident context once, uses compact references and
shorter field names, and inherits each incident's time window unless a row needs
its original spelling preserved. All selected observations/provenance, validated
context and errors remain; detailed v2 is still available via CLI --audit-export.
Local stub comparison: **247,043 → 57,345 bytes (76.8% smaller)**, not truncation.
This did not change the model, parsing or validation. Twenty-eight tests passed.

Three hosted runs launched about 55 seconds apart **overlapped**:

| Run | End-to-end seconds | Context passed/failed |
|---|---:|---:|
| 1 | 309.671 | 6/1 |
| 2 | 251.175 | 6/1 |
| 3 | 213.308 | 6/1 |

Mean 258.051s; all extracted/exported 17/7/98, but Nicollet Island context timed
out at about 90s in each. Admission was about 5.2–5.4s. These are not isolated
latency measurements, causal load tests, or evidence of cache warming.

A local-only diagnostic pod reused production context generation sequentially:
Nicollet Island (6,597-byte input) timed out at 90.061s; external service
197.43.113.112 (6,584 bytes) passed in 27.108s. Timeout reproduced without
overlap; payload size alone did not explain it. Provider/gateway/content effects
remain unproven; no causal field ablation or serving-queue breakdown was obtained.

An OS vulnerability remediation request (`libexpat1` 2.9.0-r0 → ≥2.10.0-r0) could
not be resolved in application code. Platform-managed image update/rebuild/rescan
and installed-version evidence remain outstanding; no successful patch is claimed.

## 9. Execution visibility: 0.1.15–0.1.16

**0.1.15:** application-authored stage/group messages streamed as Harness text-block
deltas with elapsed timestamps. The final tool outcome saved the same log and
file block. No uploaded strings, private reasoning or unvalidated model prose
were emitted. Thirty-one tests passed; package check ready with no blockers but
local Semgrep unavailable. A generic CLI publish failed to resolve the workspace
pod before upload; pod-specific builder publication succeeded.

Hosted SSE verified **19 live updates** with an exact durable-log match. The run
completed **103.339s**, all seven contexts passed, all 98 observations exported.
Invocation `inv_dfd0e08f-d7fc-4924-bf7b-d74282d743ec`; evidence is in
outputs/progress_verification_0.1.15.json. This was live transport evidence, not
independent browser automation.

The operator screenshot showed a timestamped wall of answer text because Markdown
collapsed line breaks. Donovan reference code accepts block_update fragments but
drops numeric progress events, so numeric progress was not a compatible shortcut.

**0.1.16:** changed live and saved progress to thinking blocks, added paragraph
spacing, removed timestamps and routine group-completed notices, and retained
explicit input/context/file failures. Status says reading, identified counts,
reviewing each group and preparing the file. No additional inference was added.
Thirty-two tests passed, including real wire models and failure preservation.

Hosted stored output verified thinking paragraphs, final status and file
`4d9933ea-0354-4022-a818-7572219adce6`. Run time **287.646s**: all 98 observations
exported; five contexts passed, two hit 90-second timeouts. A generic SSE read
stayed open and was interrupted. Verification resumed via finite status/output
reads without launching duplicate work. This run did not independently capture
live thinking-delta delivery; the operator later confirmed the revised UI works.

## 10. POC acceptance, performance interpretation and housekeeping

The operator accepted the initial POC and asked how many alerts it handles and
why timing varies. Clarified: 17 alerts/findings, seven grouped model analyses,
not 98 alerts. Recent observed runtimes ranged about 1m43s–4m48s; earlier measured
runs were slower. Two 90-second timeouts can add three minutes. Startup was only
about six seconds in the latest measured run. Evidence locates most delay in the
model-call path, but does not isolate Argon serving, provider queue or LiteLLM
gateway, or prove AMS is the cause. No latency promise or root-cause fix was made.

During housekeeping AMS reported **0.1.17 active/latest**, referencing the same
bundle file as 0.1.16: `0a858aca-e684-46e9-97cd-0961b04e7a6f`. The intervening
publication action is not explained in the available record. All **14 published
source/metadata files** were restored to ams_snapshots/0.1.17/alert_triage and
compared byte-for-byte with editable source; all match. No source overwrite,
credential export, deployment change or new live benchmark was required.

README and Donovan guidance were rewritten as current-state documents rather
than stacked contradictory changelog entries. Benchmarks gained later runs;
historical verification/review remain labeled as history. A local source-backup
record documents scope and reproducibility. The original fixture was not modified.

## Remaining work / what this POC does not establish

Subsequent organization-only change: the complete triage project (code, tests,
fixture, outputs, documentation, and AMS source snapshot) moved into
`agents/triage_agent/` to make room for separately developed agents. A shared
overview/instructions remain at `agents/`. Application source and deployment were
not changed; historical relative paths now resolve from `triage_agent/`.

- No enrichment agent, authorized resource integration, autonomous action, DNS,
  WHOIS, PCAP or SIEM/SOAR implementation.
- No production scale/load test, model-serving root cause or latency guarantee.
- No complete semantic validation or live adversarial injection certification.
- No classification propagation guarantee; review markings/access before reuse.
- Hosted export remains observation-oriented; full domain/registration inventory,
  cross-source IDs and per-row issue precision need future contract design.
- Legacy CLI default filename, import-time contract asserts, tool-denylist upkeep,
  SDK dependency footprint and some lexical false positives remain review items.
- Local Semgrep unavailable; platform base-image vulnerability remediation unresolved.
- Source backup contains application source, not a runtime image, dependencies,
  infrastructure secrets, all historical releases or all generated managed files.

See README.md for runnable current usage, BENCHMARKS.md for IDs/timing caveats,
LOCAL_BACKUP.md for preservation evidence, and REVIEW.md for original review detail.

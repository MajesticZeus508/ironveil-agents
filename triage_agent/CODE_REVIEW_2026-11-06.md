# Alert Triage Agent — Code Review (2026-11-06)

> Relocation note: the reviewed project was subsequently moved from `agents/`
> to `agents/triage_agent/`. Run historical reproduction commands from the latter
> directory (replace `cd agents` with `cd agents/triage_agent`). Review findings
> and recommendations have not been implemented by this directory move.

Scope: every file in `agents/`, including `plugins/alert_triage/`, `plugins/triage_isolation/`,
`ams_snapshots/`, `tests/`, `outputs/`, the fixture, and all seven markdown documents.
Method: read all 54 files, ran the 32-test suite, executed both documented CLI commands,
and probed the parser, narrative validator, and export with crafted inputs. Every finding
marked **Verified** was reproduced locally in this review. No files were modified.

This document is written so a code assistant can act on it. Each finding has a location,
the evidence, and a concrete change. Work items are ordered in the final section.

---

## 1. Verdict

The deterministic core is well engineered and the trust boundaries are correct:

- Python owns every fact (identifiers, indicators, enrichment labels, metrics, priority).
- The model writes narrative only; its references are checked against the input.
- Failures close instead of inventing content; provider error strings are never persisted.
- Null z-scores, zero-variance baselines, UTC grouping, conflicting finding IDs, and
  prompt-injection text in alert fields are all handled correctly.

The weaknesses are at the edges:

1. The narrative validator rejects ordinary analyst prose and discards whole analyses.
2. The documented CLI run path does not work, and a test fallback hides it.
3. Live-mode configuration errors are masked as generic model failures.
4. Seven sequential model calls with zero retries make latency the dominant complaint.
5. Export indicator IDs are not stable across inputs.
6. The handoff file is row-shaped; domains and ASN never reach it.
7. There is no version control; backups are hand-rolled directory copies.
8. Seven overlapping documentation files (~1,000 lines) describe the same state.

### Measured results

| Check | Result |
|---|---|
| Unit tests (`python -m unittest discover -s tests`) | 32 ran, 30 passed, 2 skipped (SDK absent) |
| Documented CLI default (`python triage.py --stub`, no `--input`) | `FileNotFoundError`, exit code 0 |
| Live CLI without SDK installed | 7 of 7 groups `model_request_failed`; cause hidden |
| Export ID stability after appending one unrelated finding | 0 of 98 IDs preserved |
| Export ID stability after prepending one unrelated finding | 0 of 98 IDs preserved |
| `outputs/` vs `outputs/example_stub/` | byte-identical duplicates |
| `plugins/alert_triage/` vs `ams_snapshots/0.1.17/alert_triage/` | identical except empty `fixture/` dir |

---

## 2. Findings, ranked by impact

### F1. Narrative validator rejects ordinary analyst prose — **Verified**

**Location:** `plugins/alert_triage/agent.py`, `validate_response()`, lines 92–118.
IPv6 candidate regex at line 95; domain candidate regex at line 114.

**Evidence.** Each sentence below was appended to a valid stub response and passed to
`validate_response`. Each one fails the *entire group's* analysis:

```
"Review traffic to Amazon.com and Microsoft."        -> invented domain in narrative: Amazon.com
"Sent/received ratio roughly 1:10:1."                -> malformed IP in narrative
"The host runs Node.js and e.g. Python."             -> invented domain in narrative: Node.js
"No trailing space.Review the asset owner."          -> invented domain in narrative: space.Review
```

Context-only path (`validate_context_response`), same effect:

```
"Hypothesis: CDN/update traffic from Microsoft.com and Fastly." -> invented domain: Microsoft.com
```

The exact supplied label `MICROSOFT CORP` is permitted; the natural rendering `Microsoft.com`
is not. The 0.1.12 clock-token exclusion (line 97) fixed one symptom of the IPv6 regex, not
the class of problem.

**Also verified:** a model response wrapped in a ```` ```json ```` fence raises
`JSONDecodeError` and the group is marked failed. The full-report `LiveClient` never binds a
JSON response format; only `LiveContextClient` does (lines 137–138). The CLI live path is
therefore exposed.

**Change.**
- Keep hard failure for `key_evidence` references and `highlighted_indicators`. These are
  structured and checkable.
- Downgrade the lexical IP/domain scan of free text to a recorded warning on the result
  (e.g. `narrative_warnings: [...]`), not a rejection.
- If any lexical check must stay hard: require at least one hex letter or `::` in an IPv6
  candidate; skip domain candidates whose final label is not a real TLD (small allowlist) or
  whose preceding character is a sentence-ending period followed by an uppercase letter.
- Strip leading/trailing code fences before `json.loads` in `LiveClient.analyze`, and bind a
  JSON response format for the full-report mode as well.
- Add the five probe sentences above as regression tests that must **pass**.

### F2. Documented CLI default is broken; a test hides it — **Verified**

**Location:** `plugins/alert_triage/triage.py:18` (`FIXTURE = "...jsonl"`);
`tests/test_triage.py:17–19` (fallback to `.json`); `README.md` offline example.

**Evidence.** The file on disk is `ueba_findings_sim_run2_2026-11-03.json`. Running
`python triage.py --stub` without `--input` raises `FileNotFoundError`. The test setup falls
back to `.json` when `.jsonl` is missing, so the suite stays green.

**Change.** Set `FIXTURE` to the `.json` name. Delete the fallback in `setUpClass` so the
suite fails when the default is wrong. Have `main()` return a nonzero exit and a clear
message when the input path does not exist.

### F3. Live-mode configuration failures are masked — **Verified**

**Location:** `plugins/alert_triage/triage.py`, `analyze()` exception handler;
`plugins/alert_triage/agent.py:129–136` (`LiveClient` lazy imports).

**Evidence.** Without the SDK installed, every group reports:

```json
{"stage": "model_call", "type": "ModuleNotFoundError", "code": "model_request_failed",
 "message": "Narrative call or validation failed; deterministic results preserved."}
```

Sanitizing provider errors is correct. Sanitizing a missing import or missing environment
variable is not; it produces a misleading "partial" run and costs the user time.

**Change.** Add a preflight in `main()` (before parsing input) that, in live mode, verifies
`spark_agent_kit`, `sling_agent`, and `langchain_core` import, and that
`LITELLM_PROXY_BASE_URL` is set. Exit with a named error (`missing_dependency`,
`missing_env`) and a one-line remedy. Do not run the pipeline.

### F4. Sequential model calls, zero retries, one group times out repeatedly — **Verified from records**

**Location:** `plugins/alert_triage/triage.py`, `analyze()` loop ("Sequential by design");
`plugins/alert_triage/agent.py:135` (`timeout: 90`, `max_retries: 0`).

**Evidence.** Seven calls at 15–90 s each produce runs of 103–385 s. Per `BENCHMARKS.md`, the
Nicollet Island (`site_volume`) group hit the 90 s timeout in 4 of the 5 runs where it was
tracked, including the sequential isolation diagnostic, so load is not the cause. That group
is the only one in the fixture with `zero_variance: true`, `z_score: null`, two protocols,
seven destination countries, and 19 `related_entities`. The comment "Sequential by design"
records no reason.

**Change.** None of these weaken validation:
- Run groups under bounded concurrency (`asyncio.Semaphore(3)` or 4). Expected wall time
  drops to roughly the slowest single call.
- Allow exactly one retry on **timeout only** (not on validation failure). Record
  `retried: true` in `analysis_error`/result.
- Perform the field ablation the benchmarks admit was never done. Using
  `plugins/triage_isolation/`, send the Nicollet payload (a) with `CONTEXT_RESPONSE_FORMAT`
  removed, (b) with `zero_variance`/`z_score` removed, (c) with `related_entities` truncated.
  Record which variant returns under 90 s in `BENCHMARKS.md`. Gemini's handling of
  `maxLength`/`minItems` inside a strict JSON schema is a plausible suspect.

### F5. Export indicator IDs are not stable — **Verified**

**Location:** `plugins/alert_triage/export.py`, `build_audit_export()`, lines 49–52.

**Evidence.** `indicator_id = sha256(input_sha256 + canonical(item))` where `item` includes
`occurrences` (with source line numbers) and the group's `data_quality_issues`. Appending one
unrelated finding to the fixture changed all 98 IDs; prepending did the same. In v3 the row
no longer carries `data_quality_issues`, so the ID depends on data the file does not contain.
A downstream enricher that caches by ID will never get a hit.

**Change.** Define identity from content only:
- Indicator ID: `sha256(type + ":" + normalized_value)`.
- Observation ID: `sha256(canonical(evidence_row_selected_fields + time_window))`, excluding
  source lines, file hash, and issues.
- Keep `input_sha256` in `source`, not in any ID. Version the contract as `alert-indicators/4`.

### F6. Handoff file is row-shaped; domains/ASN never exported; group issues stamped per row — **Verified**

**Location:** `plugins/alert_triage/export.py`, `build_indicator_export()`;
`plugins/alert_triage/triage.py`, `summarize()` (appends `byte_direction_assumed` to every group).

**Evidence.** `extracted_indicators.json` has 98 flow rows for 80 distinct destination IPs and
22 distinct source IPs; the enricher must re-derive the unique set. Using
`tests/fixtures/domain_and_edge_cases.json`, triage results attach ASN `64512` and two domains
to the inventory, but the export carries neither. `byte_direction_assumed` is emitted once per
group, so the report prints the same assumption seven times as a "data-quality note".
(These were raised in the 2026-11-05 `REVIEW.md` and were not adopted.)

**Change.** Export `indicators.ips[]` and `indicators.domains[]` keyed by normalized value,
each with `roles`, `address_classification`, supplied labels (company/country/ASN/org when
present), the group `review_priority`, and a list of observation references. Keep the
observation table as a secondary section. Attach data-quality issues to the indicator or row
they describe; emit run-level assumptions once at the top level.

### F7. Output redundancy — **Verified**

**Location:** `plugins/alert_triage/triage.py`, `summarize()` and `indicator_inventory()`.

**Evidence.** `triage_results.json` is 772 KB indented (458 KB compact) for 17 findings. Each
evidence row appears in `sample_summary.evidence`, again in `indicators.observations`, and
again inside each IP's `occurrences`. For the first group: `indicators` is 26 KB,
`sample_summary` 6 KB, `detector_metrics` 0.5 KB.

**Change.** Store deduplicated evidence rows once per group with an index; have
`sample_summary.largest_sent_byte_rows`, `indicators.observations`, and IP `occurrences`
reference the index.

### F8. Hygiene items — all **Verified**

| # | Location | Issue | Change |
|---|---|---|---|
| 8a | `agents/` (root) | Not a git repository. `ams_snapshots/0.1.17/` is a manual copy of 14 files byte-identical to `plugins/alert_triage/`; `LOCAL_BACKUP.md` is a hand-written hash table. | `git init`, commit, tag `v0.1.17`. Delete `ams_snapshots/`, `LOCAL_BACKUP.md`, and the hash table. |
| 8b | `outputs/example_stub/` | Byte-identical to `outputs/`. | Delete one. Keep `outputs/progress_verification_0.1.15.json` as evidence. |
| 8c | `plugins/alert_triage/fixture/` | Empty leftover directory; `test_uploaded_file_read_and_no_fallback` checks it. | Delete the directory. |
| 8d | `plugins/alert_triage/contracts.py:68` | `verify_contract()` runs `assert`s at import time; vanish under `python -O`, break import on failure. | Move to `tests/`. |
| 8e | `plugins/alert_triage/graph.py:46` | Scaffold tools withheld by denylist; a new tool in the next `sling-agent` release is enabled by default. | `tools=[make_triage_tool(WORKDIR)]` only, or an explicit allowlist. |
| 8f | `plugins/alert_triage/graph.py:21`, lines 12–14 | Unused `HarnessOutputSchema` import; docstring describes a bundled `fixture/` removed in 0.1.3. | Remove import; rewrite docstring. |
| 8g | `plugins/alert_triage/export.py:93` | Evidence index parsed with `occurrence["evidence_path"][9:-1]`. | Store the integer index at extraction time, or use `re.fullmatch(r"evidence\[(\d+)\]", ...)`. |
| 8h | `plugins/alert_triage/triage.py`, `utc()` and callers | Timestamps compared as ISO strings. Works today only because `+` sorts before `.`; fragile. | Have `utc()` return `datetime`; compare objects; format for output. |
| 8i | `plugins/alert_triage/hosted.py:23, 30` | Reads with `max_bytes=1_000_000` then checks `len(raw) > 1_000_000`. If the client truncates rather than errors, an oversized upload parses as a broken last record. | Read `max_bytes=1_000_001` and reject when `len(raw) > 1_000_000`. |
| 8j | `plugins/alert_triage/triage.py`, `validate_finding()` | Trailing space in `measures` drops the record; `severity: "High"` is accepted and silently becomes `unknown` priority; an FQDN in `entity.id` is extracted as neither IP nor domain. | Normalize whitespace/case with a `normalized_field` warning; treat a dotted non-IP `entity.id` as a domain candidate. |
| 8k | `plugins/alert_triage/triage.py`, `render_report()` | Prints `34.0 distinct external destinations`; `protocol_mix` line never names `entity.protocol`; data-quality notes rendered as escaped raw JSON. | Format integers; include protocol; render issues as sentences. |
| 8l | `plugins/alert_triage/requirements.txt` | Pulls a coding-agent framework and ripgrep for a stdlib-only deterministic pipeline; comment says "never hand-write". | Add a stdlib-only `requirements-cli.txt` (empty or `# none`); keep scaffold file for the hosted pod. |
| 8m | `plugins/alert_triage/agent.py:130` | CLI `LiveClient` imports `sling_agent.coding.with_billing` solely for a header helper. | Inline the header or make the import optional. |

### F9. Documentation sprawl and drift

**Location:** `README.md`, `BUILD_STATUS.md`, `SESSION_HISTORY.md`, `REVIEW.md`, `DONOVAN.md`,
`INDICATOR_CONTRACT.md`, `BENCHMARKS.md`, `LOCAL_BACKUP.md`, `agents.md`.

**Evidence.** About 1,000 lines across eight files, with the same facts (17/7/98 counts,
0.1.17 status, invocation IDs, "operator confirmed") repeated in four or five places.
`agents.md` (the brief) still says "no platform integration, no multi-agent framework, two
Python files"; the repo is a 14-module hosted Agent Kit pod. `README.md` says the historical
CLI default still names `.jsonl` instead of fixing it.

**Change.** Keep three documents:
- `README.md`: current state, setup, one run example, model config, limits.
- `INDICATOR_CONTRACT.md`: the current handoff schema only; move v1/v2 history to the changelog.
- `CHANGELOG.md`: fold `BUILD_STATUS.md`, `SESSION_HISTORY.md`, `LOCAL_BACKUP.md`, and the
  2026-11-05 `REVIEW.md` into one chronological file.
Move `DONOVAN.md` and `BENCHMARKS.md` under `docs/`. Rewrite `agents.md` to describe what was
actually built so future reviewers hold the work to the right bar.

---

## 3. What is working well (do not change)

- Code/model responsibility split; model output limited to narrative fields.
- Per-occurrence provenance: `finding_id`, source line, field path, role on every indicator.
- Destination `company`/`country` labels stay attached to the correct IP; conflicts flagged.
- Exact duplicate evidence rows merged with all references retained; overlapping detectors
  never summed.
- Conflicting contents under one `finding_id` quarantined, not silently resolved.
- Null z-score and zero-variance baseline preserved as null/zero; no division by zero.
- Alert strings escaped before Markdown rendering; embedded instructions treated as data.
- Provider exceptions never persisted; credentials cannot leak into reports.
- Deterministic path is stdlib-only; test suite runs in under a second.
- Hosted path: file-first middleware removes outer provider calls; attachments exposed only on
  confirmed write; no fallback to stale uploads.

---

## 4. Ordered work plan

Items 1–4 are roughly one day and remove the most visible defects.

1. **Run path and errors (F2, F3, F1-fence).** Fix `FIXTURE`; remove the test fallback;
   add live-mode preflight; strip JSON fences and bind a response format for full mode.
   Rerun the suite.
2. **Validator (F1).** Downgrade lexical IP/domain scans to warnings. Add the five probe
   sentences as passing regression tests.
3. **Latency (F4).** Bounded concurrency (3–4), one timeout-only retry, Nicollet ablation.
   Record results in `BENCHMARKS.md`.
4. **Repository hygiene (F8a–c).** `git init`, commit, tag `v0.1.17`; delete
   `ams_snapshots/`, `outputs/example_stub/`, `plugins/alert_triage/fixture/`.
5. **Handoff redesign (F5, F6).** Indicator-keyed export with content-derived stable IDs,
   domains and registration attributes included, issues attached where they belong.
   Version as `alert-indicators/4`; add migration notes.
6. **Output slimming (F7).** Evidence rows stored once per group; references by index.
7. **Small fixes (F8d–m).** Import-time asserts, tool allowlist, stale docstring, index
   slicing, datetime comparison, size-check order, parser normalization, report formatting,
   CLI requirements file.
8. **Documentation consolidation (F9).** Three current-state files plus a changelog; rewrite
   `agents.md`.

---

## Appendix A. Reproduction commands

```sh
cd agents
python3 -m unittest discover -s tests            # 32 ran, 2 skipped without SDK
python3 triage.py --stub                           # FileNotFoundError (F2)
python3 triage.py --input ueba_findings_sim_run2_2026-11-03.json --output-dir /tmp/live
                                                   # 7/7 ModuleNotFoundError masked (F3)
cmp outputs/triage_results.json outputs/example_stub/triage_results.json   # identical (F8b)
diff -rq plugins/alert_triage ams_snapshots/0.1.17/alert_triage --exclude=__pycache__  # only fixture/ (F8a)
```

Validator probe (F1), run from `plugins/alert_triage/`:

```python
import asyncio, sys; sys.path.insert(0, '.')
from triage import parse_jsonl, group_findings, summarize
from agent import StubClient, validate_response
recs, _ = parse_jsonl(open('../../ueba_findings_sim_run2_2026-11-03.json').read())
g = group_findings(recs)[0]; s = summarize(g)
base = asyncio.run(StubClient().analyze(g, s))
for p in ["Review traffic to Amazon.com and Microsoft.", "Sent/received ratio roughly 1:10:1.",
          "The host runs Node.js and e.g. Python.", "No trailing space.Review the asset owner."]:
    r = dict(base); r["summary"] = base["summary"] + " " + p
    try: validate_response(r, g, s); print("PASS  ", p)
    except Exception as e: print("REJECT", p, "->", e)
```

ID stability probe (F5), run from `agents/`:

```python
import sys, json, copy, asyncio; sys.path.insert(0, 'plugins/alert_triage')
from triage import analyze; from export import build_indicator_export; from agent import StubClient
content = open('ueba_findings_sim_run2_2026-11-03.json').read()
a = asyncio.run(analyze(content, StubClient()))
extra = json.loads(content.splitlines()[0]); extra.update(finding_id="zz-new", incident_key="host:10.99.99.99@x")
extra["entity"]["id"] = "10.99.99.99"
b = asyncio.run(analyze(content.rstrip("\n") + "\n" + json.dumps(extra) + "\n", StubClient()))
ia = {r["id"] for r in build_indicator_export(a)["indicators"]}
ib = {r["id"] for r in build_indicator_export(b)["indicators"]}
print(f"ids preserved: {len(ia & ib)} of {len(ia)}")   # 0 of 98
```

## Appendix B. Fixture facts used in this review

| Fact | Value |
|---|---|
| Findings | 17, schema `swoop-ueba-finding/1`, source `swoop/valhalla/simulated` |
| Incident groups | 7 |
| Deduplicated evidence observations | 98 |
| Detectors | fanout 5, protocol_mix 5, geo_spread 2, company_spread 2, egress_volume 1, fan_in 1, site_volume 1 |
| Entity types | host 15, external_service 1, site 1 |
| Severities | high 9, medium 5, low 3 |
| Evidence rows per finding | 10 (15 findings), 7 (2 findings) |
| Fixture SHA-256 | `6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a` |

---

## Appendix C. Agent response and recommended priorities

**Status: recommendations for operator review, not approved implementation work.**
The original review above is preserved unchanged. This response follows a read-only
check of its principal findings against the current source. No application code or
deployment was changed; this appendix records the assessment requested by the operator.

### Overall assessment

This is a useful, largely accurate review, but I would not implement every
recommendation exactly as written. It correctly distinguishes a sound POC
foundation from weaknesses that matter before broader use.

The strongest parts should stay:
- Python owns extracted facts and provenance.
- Model-generated context is kept separate.
- Failed analyses do not fabricate successful results.
- Uploads and file creation have explicit trust boundaries.

The review identifies real technical debt. Some resulted from incremental
development: compatibility and evidence were preserved while features were added,
rather than periodically simplifying the implementation. The broken CLI default
and duplicated documentation are fair criticisms of that approach.

### 1. CLI and configuration errors — agree strongly

The `.jsonl` default is wrong, and the test fallback conceals it. Missing SDK
packages or endpoint configuration should produce one clear setup error, not
seven apparent model failures. These are small, low-risk fixes worth doing first.

I independently confirmed the default CLI fails. One correction to the review:
**it exits with code 1, not 0**. The current README's explicit
`--input ...json` example is valid; the default is broken.

### 2. Narrative validation — agree with the problem, not blanket relaxation

I reproduced the reported false positives for ratios, `Node.js`, and joined
sentences. Rejecting an entire incident analysis because of punctuation is too
brittle. However, I would not make every invented IP/domain a warning:

- `1:10:1` is plainly a ratio and should not fail.
- `Node.js` can be ordinary product terminology.
- `Microsoft.com` is genuinely a domain. A supplied company label of
  `MICROSOFT CORP` does not authorize the model to invent that domain as an
  investigation target.

Distinguish ambiguous lexical matches from clear unsupported indicators,
preserving strict checks for the latter. Tests should cover both false positives
and invented indicators, not require every review example to pass automatically.

I support structured JSON output for full-report mode. Accepting an exact
enclosing JSON code fence is reasonable, provided validation still rejects extra
prose or invalid content.

### 3. Version control — agree, but preserve evidence first

Git should replace directory copies as the primary development history. But I
would not immediately delete the downloaded AMS snapshot and backup evidence.
Those establish what was actually published, which a new Git commit alone does
not prove.

Initialize version control, exclude generated/cache files, preserve the
deployment-source comparison, and then decide what should be archived. No need
to rush deletion.

### 4. Latency — experiment before changing concurrency and retries

Bounded concurrency is worth testing, but several review conclusions overreach:

- Reproducing a timeout without overlapping local runs does not rule out shared
  provider or gateway load.
- With seven groups and concurrency three, runtime is not simply the slowest
  single call; multiple scheduling waves remain.
- A timeout retry can improve completion, but also add another 90 seconds and
  additional inference cost.

Measure concurrency one versus two, holding other settings constant, before
trying three or four. Test retries separately with an overall time budget.

The suggested ablation is sensible, but `related_entities` is already absent
from the compact hosted payload. Truncating it would not test the current
request. Experiments must inspect what is actually sent.

### 5. Stable IDs and enrichment-oriented export — agree before the next agent

The existing IDs are source-specific, not cross-file indicator identities. That
is documented, but it is unsuitable for downstream caching. Separate:

- Indicator identity: IP/domain type plus normalized value.
- Observation identity: the relevant evidence content.
- Provenance: source file, finding, and occurrence references.

Hashing only the currently selected fields could collapse observations that
differ in evidence time or other meaningful fields. Define those semantics
before introducing schema v4.

Exporting domains and explicitly supplied registration attributes is important
before an enrichment agent consumes this file. It is less urgent for the current
standalone demonstration.

### 6. Hygiene and documentation — mostly agree

I support moving import-time test assertions into tests, explicit tool exposure
rather than relying only on a denylist, clearer report formatting, documentation
consolidation, and updated project instructions.

Qualifications:
- Do not treat every dotted entity ID as a domain without schema/type guidance.
- Verify file-client oversize behavior before assuming truncation.
- Do not inline platform billing headers merely to remove a dependency.
- An empty fixture directory is not an important defect by itself.

Documentation should be simplified, but the operator-requested historical
account should remain available, perhaps under `docs/history/`, rather than
being deleted.

### Recommended implementation order

1. CLI/default-path fixes and setup preflight.
2. Targeted validator repairs with positive and negative regression tests.
3. Git and clearer current project instructions.
4. Controlled latency experiments.
5. Schema v4 design before downstream enrichment.
6. Internal output deduplication and documentation consolidation.

**Bottom line:** act on the review in small, independently tested changes, not
one sweeping refactor. The POC is useful; the next step should improve reliability
and maintainability without weakening its grounding guarantees. The operator will
decide which changes to authorize now.

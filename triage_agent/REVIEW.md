# Alert Triage Agent — Code Review

> Historical review of an earlier implementation (18 tests), not a fresh audit of
> 0.1.17. Later changes added schema-constrained context, clock-token handling,
> compact incident-level v3 export and current documentation. Several concerns
> remain, including source-dependent IDs, observation-only export, lexical false
> positives and tool-denylist maintenance. See SESSION_HISTORY.md and README.md.

Date: 2026-11-05
Scope: `plugins/alert_triage/` (triage, agent, export, hosted, graph, contracts), `tests/`, docs, and the generated `outputs/`.
Method: read every module, ran the 18-test suite (all pass), ran the CLI in stub and live modes, and probed the validator and export with scripted inputs. Every finding below was reproduced, except the one marked unverified.

## Overall

The deterministic core is in good shape. Code owns every fact and the model only writes narrative. Evidence references are checked against a catalog built from the input. Failures are fail-closed with sanitized errors. Overlapping evidence is deduplicated without being double counted. Null z-scores, zero-variance baselines, UTC grouping, conflicting finding IDs, and injection text in alert fields are all handled correctly.

Three areas need work before the next agent consumes this output:

1. The handoff file (`extracted_indicators.json`) is shaped for a report, not for an enricher.
2. The narrative validator rejects ordinary analyst prose, discarding whole group analyses.
3. The run path and docs no longer match the code.

## 1. Handoff file is shaped for a report, not for an enricher

**Row-oriented, not indicator-oriented.** The export has 98 flow rows covering 80 distinct destination IPs and 22 distinct source IPs. An enrichment agent must re-derive the unique IP set itself. The per-IP inventory already computed in `triage_results.json` (roles, private/global classification, attached company/country labels, conflict flag) is not exported.

**Domains and registration attributes never reach the export.** Using `tests/fixtures/domain_and_edge_cases.json`, triage results attach the supplied ASN to `88.116.5.17` and list two domains. The export contains no domain items and no ASN field. Only the nine evidence columns are exported.

**Group-level issues are stamped onto every row.** In the `192.168.194.160` group, two destination IPs carry conflicting company labels and four rows involve them. All 18 exported rows are flagged `conflicting_enrichment`. One unsupported severity on one finding flags all 17 rows of its group with `unknown_severity`. The consumer cannot tell which row an issue belongs to.

**Byte-direction assumption attached to all 98 rows.** `byte_direction_assumed` is a run-level assumption, not a per-row defect. It appears on every export row and in every report section's data-quality notes, drowning out real issues.

**`indicator_id` is not stable.** It hashes the input file hash plus occurrences plus group issues. Adding one unrelated finding to the input changed every existing ID (0 of 24 preserved). If the enricher caches results by ID across runs, it will never get a cache hit.

**No priority, severity, detector, or entity on export rows.** The enricher cannot order its work. `incident_key` encodes the entity but review priority is absent.

**Size and repetition.** 224 KB for 17 findings, mostly the same `interpretation` string and assumption text repeated 98 times.

**Evidence `time` is part of the dedupe key but not exported.** No collisions in the current fixture, but two rows that differ only by time would look like exact duplicates to the consumer. `egress_band` and `bytes_sent_z_score` are also dropped; if intentional, say so in `INDICATOR_CONTRACT.md`.

**Recommendation.** Export `indicators.ips` and `indicators.domains` keyed by normalized value. Give each one its roles, supplied labels, address classification, registration attributes when supplied, the group's review priority, and a list of observation references. Attach data-quality issues to the indicator or row they describe; keep run-level assumptions at the top once. Give indicators an identity of type plus normalized value and give rows a separate observation ID. Keep the observation table as a secondary section if the enricher needs flows.

## 2. Narrative validator rejects ordinary analyst prose

Each fragment below was appended to a valid stub response and passed through `validate_response`. Each one fails the entire group's narrative:

| Prose fragment | Error raised |
|---|---|
| "began at 10:32:28" | malformed IP in narrative (IPv6 regex matches hh:mm:ss) |
| "deterministic_result.indicators.observations" | invented domain in narrative: indicators.observations |
| "Amazon.com" | invented domain in narrative (only the exact label `AMAZON.COM INC` is allowed) |
| "ratio roughly 1:10:1" | malformed IP in narrative |

The second phrase is copied verbatim from the prompt in `agent.py`. The prompt also instructs the model to cite evidence times, which are hh:mm:ss values. `BUILD_STATUS.md` already records live probes that failed closed on lexical domain checks.

**Fenced JSON fails.** A model response wrapped in a ```` ```json ```` code fence fails with `JSONDecodeError` and the group is marked failed. Gemini frequently fences output unless a JSON response format is requested.

**Recommendation.** Keep hard failure for catalog references and highlighted indicators. Turn the lexical IP and domain scans into warnings recorded on the result. If they stay hard, ignore IPv6 candidates with no hex letters and no `::`, and whitelist tokens that appear in the prompt or in payload keys. Request a JSON response format from the gateway, or strip code fences before parsing.

## 3. Run path, docs, and scope

**The README run command does not work.** It references `ueba_findings_sim_run2_2026-11-03.jsonl`. The file on disk is `.json`. The CLI default and the `FIXTURE` constant both point at the missing name. The tests quietly fall back to `.json`, which is why this went unnoticed.

**Live mode without the SDK hides the cause.** All seven groups fail with the generic "Narrative call or validation failed" message and a `ModuleNotFoundError` type. Add a preflight that checks environment variables and imports before any work and names what is missing.

**README contradicts itself.** The top says Gemini Argon; the Local run section says `openai/gpt-5.4`. One section says no downloadable artifacts exist; another says the tool creates an attachment. The file is a stack of changelog entries marked "supersedes below". Rewrite as a current-state document and move history to a CHANGELOG.

**requirements.txt is wrong for the CLI.** The deterministic pipeline is stdlib-only, yet the file pulls a coding-agent framework and ripgrep, with a comment saying "never hand-write this file". Split into a stdlib core and an optional hosted extra.

**Scope has moved past AGENTS.md.** The brief says no platform integration, no multi-agent framework, and two Python files. The repo now has a Harness contract, a CompletionAgent built from a coding scaffold, Donovan file blocks, Gemini middleware filtering, and a persona module. That may be the right call, but update AGENTS.md so reviewers hold the work to the right bar.

**Tools are withheld by denylist.** `graph.py` disables ten named tools from the coding scaffold. Any new tool in a future release is enabled by default. Build the agent with only `run_triage`, or use an allowlist.

**`contracts.py` runs asserts at import time** in production. Under `python -O` they vanish, and a failure breaks the import. Move them to the test suite.

**Validation is brittle for a pipeline input.** A trailing space in `measures` drops the whole record. Acceptable against this fixture, risky once real detector output arrives. Consider accepting cosmetic drift with a warning.

**Report cosmetics.** Counts print as floats ("152.0 distinct external destinations"). The protocol_mix line never names the protocol even though `entity.protocol` is present. Data-quality notes render as escaped raw JSON.

**Unverified.** In `hosted.py` the 1 MB size check runs after a read capped at 1 MB. If the file client truncates instead of erroring, an oversized upload parses as a broken last line rather than a size error. The SDK was not available locally to confirm its behavior.

## What is working well

- Clear split: Python owns identifiers, metrics, indicators, priority, and statistics; the model supplies narrative only.
- Every indicator occurrence carries finding ID, source line, field path, and role. Destination labels stay attached to the correct IP.
- Exact duplicate evidence rows are merged with all references retained, and overlapping detectors are not summed.
- Conflicting finding IDs are quarantined rather than silently resolved.
- Provider exceptions are never persisted, so credentials cannot leak into reports.
- Alert strings are escaped before Markdown rendering; embedded instructions are treated as data.
- The deterministic pipeline has no third-party dependencies and the test suite runs in under a second.

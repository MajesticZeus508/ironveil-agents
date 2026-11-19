# Documentation map and maintenance policy

Updated 2026-11-18. Current documentation is separated from dated evidence without
moving source, fixtures, receipts or published snapshots.

## Read in this order

| Need | Authoritative starting point |
|---|---|
| Project status and roles | [Workspace README](../README.md) |
| Run the entry / troubleshoot | [Operator runbook](../DEMO.md) |
| Architecture, both handoffs and integrity | [WORKFLOW.md](WORKFLOW.md) |
| Latest deployed test and storage diagnosis | [Diagnostic release](DIAGNOSTIC_RELEASE_2026_11_18.md) |
| Test counts and historical benchmark comparison | [Evaluation](../EVALUATION.md) |
| Version/source IDs and backup gaps | [AMS inventory](../AMS_INVENTORY.md) |
| Triage schema / UI | [Indicator contract](INDICATOR_CONTRACT.md), [Donovan](DONOVAN.md) |
| Enrichment receiver / AWS future work | [AMS handoff](../enrichment_agent/AMS_HANDOFF.md), [S3 integration](../enrichment_agent/S3_INTEGRATION.md) |
| Reporting receiver / analysis controls | [Contract](../recommendation_agent/CONTRACT.md), [verification](../recommendation_agent/VERIFICATION.md) |
| What this cleanup changed | [Housekeeping](../HOUSEKEEPING.md) |

## Current versus historical

Agent READMEs, current contracts and the documents above are operating guidance.
Version/status assertions are **dated checkpoints**, not live monitoring.
Reporting means the Recommendations agent, not a fourth deployed agent.

Dated release, compatibility, review, benchmark and verification entries retain
their original results, including failed publishes and “unpublished” local phases.
Read newer entries first. In particular, the Nov 17 ARP authentication blocker was
resolved on an explicitly requested retry; the structured releases went active.
Nov 18 diagnostics then identified missing sandbox SGP configuration. These are
different failures. Older successful five-file runs do not prove current storage.

`STRUCTURED_ENRICHMENT_HANDOFF.md` is the historical caller implementation record;
`SEQUENTIAL_HANDOFF.md` is the earlier file-based integration record. Their old
file gates are not current structured-chain prerequisites. `LUX_*PLAN*` and the
Enrichment MITRE integration plan are proposals/checkpoints, not approval for more
integration. Review recommendations are not automatically authorized work.

## Source and evidence ownership

- Triage editable source: `plugins/alert_triage/`, **Dev-targeted** receiver IDs.
  Current isolated staging source: `releases/staging_0_1_30/`, adjacent provenance.
  Use `tests/prepare_staging_release.py` for an approved new staging release;
  never publish the Dev tree to staging or edit an existing release in place.
- Enrichment core: root `contracts.py`, `enrich.py`, `history.py`; stage with
  `prepare_pod.py`, verify `--check`. Hosted-specific code is owned in `ams/`.
- Reporting implementation: owned directly in `../recommendation_agent/ams/`.
  No separate staging/copy script.
- `releases/`, `ams_snapshots/`, generated `outputs/`, raw hosted JSON receipts and
  provenance are retained evidence. Do not rewrite, rename or regenerate them to
  match today's narrative. Source backup is still incomplete.
- Pod-contained READMEs are bundled source: leave their release bytes unchanged
  during documentation-only cleanup; parent documentation supersedes old wording.
- Keep agent-specific additions inside their owning agent directory. Root docs
  describe shared operation. Unrelated `icons/`, `lux/`, `projects/` work is not
  reorganized by this task. Existing uncommitted implementation work is preserved.

## Updating this documentation

For a future approved release, update the root version table/runbook/inventory,
the owning agent README, current contract if changed, and a dated release ledger.
Keep test evidence labeled by runtime and scope; do not merge one-incident
diagnostics with seven-incident performance samples or claim unknown scans passed.
Record source IDs and invocation IDs, not credentials, environment values, signed
URLs, provider error bodies or raw configuration dumps.

Check links/fences with `python3 -B triage_agent/tests/check_documentation.py`
from the workspace root and run `git diff --check`. The checker does not validate
external links, anchors, prose accuracy or generated reports. No publish, model
test, platform mutation or commit is implied by documentation housekeeping.

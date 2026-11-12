# IronVeil Agents

Network investigation proof-of-concept agents for alert triage, historical
enrichment, and analyst recommendations. Each agent's source, tests, examples,
and documentation live in its own directory.

## Team handoff

ScaleGov **staging**, tenant **platform** (`6a1099f9e1ca37ee1216d8c3`).
Live AMS inventory rechecked during housekeeping; evaluation timestamps extend
through **2026-11-11 UTC**. Dates in older filenames are retained as evidence.

| Agent | Active/latest | Local staging implementation | Role |
|---|---|---|---|
| Network Investigation Demo | **0.1.24** | `triage_agent/releases/staging_0_1_24/` | Entry; deterministic extraction and five-stage orchestration |
| Historical Enrichment POC | **0.1.3** | `enrichment_agent/ams/` | History criteria; AWS **not configured** |
| Recommendation Agent POC | **0.1.4** | `recommendation_agent/ams/` | Argon incident assessments; human review, no actions |

**Do not publish Triage's editable `plugins/alert_triage/` directly to staging:**
it targets Dev receivers. The isolated staging release is retained separately.
Local source presence is not a fresh byte-for-byte AMS bundle verification.

## Read first

- [Operator runbook](DEMO.md): input, outputs, controls and troubleshooting.
- [Team evaluation summary](EVALUATION.md): fresh offline tests and hosted outcomes,
  including failures—not just the earlier successful demonstration.
- [AMS inventory and backup gaps](AMS_INVENTORY.md): all seven visible agents,
  source-bundle IDs, local coverage and recovery instructions.
- Agent details: [Triage](triage_agent/README.md),
  [Enrichment](enrichment_agent/README.md),
  [Recommendation](recommendation_agent/README.md).

Latest five-run hosted evaluation: all five chains reached every stage and
returned five files each; **28/35 Recommendation analyses succeeded (80%)**.
Six timed out and one failed validation. Median end-to-end time **190.490s**;
only one of five runs achieved 7/7 analyses. This is exploratory evidence, not an SLA
or a semantic-quality score. All application runs remain `partial` because AWS
history is unavailable and Triage narrative is intentionally deferred.

## Open boundaries

- Security remediation is **not independently attested**. New rebuilt images and
  active/no-compromise fields do not replace a final-image scan/SBOM.
- Synthetic demo data only; marking propagation remains unresolved.
- No live AWS/history, external intelligence lookup or autonomous response.
- **Backup is incomplete:** older VoF agents, current downloaded source snapshots
  and hosted output files still need binary-safe recovery; see the inventory.

Historical reviews, release ledgers, snapshots and generated reports are retained.
They describe their own checkpoints, not current deployment status. No deployment,
metadata, credential or Git changes were made for this cleanup.

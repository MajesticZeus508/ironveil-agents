# IronVeil Agents

Network investigation proof-of-concept agents for alert triage, historical
enrichment, and analyst recommendations. Each agent's source, tests, examples,
and documentation live in its own directory.

## Start here

**Dev update (2026-11-19):** IronVeil Triage **0.1.31**, Enrichment **0.1.6**,
Recommendations **0.1.10** are published and freshly rechecked active/latest in
Dev tenant `69dfa4b844ff488d98b2674f`. Explicit platform-managed
`platform-sgp-runtime-http-v8` access cleared the tested file-write blocker:
Triage created one file and direct receiver tests created all four downstream
exports, with confirmed attachments and metadata/readback evidence. **Automatic
Dev orchestration is not fixed:** the LUX chain stopped before Enrichment with
`structured_handoff_unavailable`. Staging was not changed or freshly retested.
See [Dev release](triage_agent/DEV_SGP_V8_RELEASE_2026_11_19.md),
[Triage acceptance](triage_agent/DEV_SGP_V8_ACCEPTANCE_2026_11_19.md), and
[downstream verification](triage_agent/DEV_DOWNSTREAM_WRITES_2026_11_19.md).

**Open IronVeil Investigation — Start Here in Donovan staging and upload your
findings.** It performs triage, calls Historical Enrichment, then calls
Recommendations automatically. You do not need to run the supporting agents
separately. Follow the [operator runbook](DEMO.md) for the upload and prompt.

**Proof of concept:** use approved synthetic data only. AWS history is not
connected; human review is required and no response actions are executed.

```text
Findings upload
      ↓
IronVeil Investigation — Start Here
      │  Triage and indicator extraction
      ↓
IronVeil Historical Enrichment       (called automatically)
      ↓
IronVeil Recommendations             (called automatically)
      ↓
Analyst reports returned through the entry point
```

Both internal handoffs now pass explicit, canonical-hashed JSON objects, not
intermediate files or model-rewritten prose. Managed files remain analyst exports,
not prerequisites for downstream analysis. See [architecture](triage_agent/WORKFLOW.md).

**Staging storage blocker (2026-11-18):** all three deployed agents report
`missing_sgp_configuration`; missing/blank `SGP_API_URL` stops uploads **before
dispatch**. The latest structured chain completed analysis but returned **no
confirmed attachments**, correctly marked INVESTIGATION INCOMPLETE. Platform
runtime configuration needs repair; production has not been tested, so this is
confirmed in staging, **not proven staging-only**. [Diagnosis](triage_agent/DIAGNOSTIC_RELEASE_2026_11_18.md).

### Where the code lives

| Directory | Purpose |
|---|---|
| [`triage_agent/`](triage_agent/README.md) | **Entry point, orchestration, and triage implementation** |
| [`enrichment_agent/`](enrichment_agent/README.md) | Supporting historical enrichment agent |
| [`recommendation_agent/`](recommendation_agent/README.md) | Supporting analyst recommendations agent |

Directory names are retained for stable paths. The entry point was formerly
**Network Investigation Demo**; older release records retain that name.

## Team handoff

ScaleGov **staging**, tenant **platform** (`6a1099f9e1ca37ee1216d8c3`).
Three-agent release and hosted verification checkpoint: **2026-11-18 UTC**.
The wider seven-agent inventory retains its older checkpoint. This documentation
pass does not launch another hosted run or claim a fresh infrastructure audit.

| Agent | Active/latest | Local staging implementation | Role |
|---|---|---|---|
| **IronVeil Investigation — Start Here** | **0.1.30** | `triage_agent/releases/staging_0_1_30/` | **User-facing entry point**; file/LUX input, extraction and orchestration |
| IronVeil Historical Enrichment | **0.1.5** | `enrichment_agent/ams/` | Structured v3 receiver/result; AWS **not configured** |
| IronVeil Recommendations | **0.1.9** | `recommendation_agent/ams/` | Structured enrichment receiver; analyst assessments; human review, no actions |

**Do not publish Triage's editable `plugins/alert_triage/` directly to staging:**
it targets Dev receivers. The isolated staging release is retained separately.
Local source presence is not a fresh byte-for-byte AMS bundle verification.

## Read first

- [Operator runbook](DEMO.md): input, outputs, controls and troubleshooting.
- [Documentation map](triage_agent/DOCUMENTATION.md): current guidance versus
  historical evidence, source ownership and next-session reading order.
- [Workflow and handoffs](triage_agent/WORKFLOW.md): exact envelopes, receipts,
  checkpoints, limits and the separation of analysis from file exports.
- [Team evaluation summary](EVALUATION.md): fresh offline tests and hosted outcomes,
  including failures—not just the earlier successful demonstration.
- [AMS inventory and backup gaps](AMS_INVENTORY.md): all seven visible agents,
  source-bundle IDs, local coverage and recovery instructions.
- Agent details: [Triage](triage_agent/README.md),
  [Enrichment](enrichment_agent/README.md),
  [Recommendation](recommendation_agent/README.md).

Latest diagnostic chain: both structured handoffs verified, **1/1 analysis**, no
confirmed files; all three writes stopped at missing runtime SGP configuration.
Latest full SDK suites: **151 passed, zero skips** (91/34/26).

Historical five-run hosted evaluation (2026-11-11, older versions): all five chains reached every stage and
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
They describe their own checkpoints, not current deployment status. On 2026-11-12,
the three staging display names and descriptions were updated to clarify roles;
agent IDs, versions, source bundles, discovery metadata and workflow behavior
were unchanged. On 2026-11-19 the three Dev display names were aligned with
staging; historical release artifacts retain their original names.

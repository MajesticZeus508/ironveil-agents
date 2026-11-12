# Historical network enrichment agent — offline core and AMS receiver

> **Current staging: 0.1.3 active/latest**, independently rechecked in AMS.
> Rebuilt after the operator-reported platform fix; its recorded image digest
> differs from the flagged predecessor. **Remediation is not independently
> attested** without a final-image scan/SBOM. Earlier takedown evidence is retained.
> See [release retry evidence](AMS_RELEASE.md) and
> [image security investigation](IMAGE_SECURITY_2026-11-10.md).

Consumes the Alert Triage agent's `alert-indicators/3` handoff and searches
historical network records to answer **whether an indicator or a defined activity
tuple was seen before**. The original triage agent is preserved.

This version is operational against local JSON historical-data fixtures/subsets.
AWS is not connected. The history-adapter boundary is ready for an S3-backed query
implementation once storage format, field mapping, access and coverage are known.
The deployed receiver source is in `ams/`. **Historical Enrichment POC 0.1.3**
is active/latest at live recheck; v3 receipt and managed outputs are
verified. See [AMS_RELEASE.md](AMS_RELEASE.md) for agent ID and test evidence.
It does not claim to reproduce a detector's anomaly or establish benign/malicious
activity. No model or external intelligence service is required.

Fresh offline regression: **24 discovered, 22 passed, two SDK skips**; core
freshness passed. Latest five-chain hosted evaluation retained history unavailable
and confirmed both Enrichment exports each time. See [team evaluation](../EVALUATION.md)
and [local backup gaps](../AMS_INVENTORY.md). No fresh source-bundle byte comparison is claimed.

## Returning to this project

Start with **[S3_INTEGRATION.md](S3_INTEGRATION.md)**: session checkpoint, data-team
intake checklist, schema/query decisions, precise implementation edit points,
test/release gates and a copy/paste prompt for the next session.
`AGENTS.md` records maintenance boundaries. No database schema or query language
has been selected; the 323 prepared requests are logical criteria, not SQL or
executed AWS queries. Automatic Triage → Enrichment → Recommendation handoffs
are implemented by the entry agent; see [current runbook](../DEMO.md).

## Run the synthetic example

Python 3.11+; standard library only. From `enrichment_agent/`:

```sh
python3 enrich.py --input fixtures/triage_v3.json --history fixtures/history.json --context fixtures/context.json --output-dir outputs/demo
python3 -m unittest discover -s tests -v
```

All fixtures are synthetic. The optional context file supplies explicit domain
and registration test attributes; those are not present in the v3 handoff.

Use a real triage export with a local historical dataset:

```sh
python3 enrich.py --input ../triage_agent/outputs/extracted_indicators.json --history fixtures/history.json --lookback-days 30 --output-dir outputs/triage_compatibility
```

That command tests compatibility using **synthetic** history, not actual network
coverage. To exercise explicit AWS-pending outcomes:

```sh
python3 enrich.py --input fixtures/triage_v3.json --aws-pending --output-dir outputs/aws_pending
```

Outputs: `enrichment_results.json` (full provenance and query details) and
`enrichment_report.md` (readable results). Use a fresh output directory each time;
existing artifacts are not overwritten. Exit 0 = completed, 2 = partial/empty,
1 = validation or file-access failure. An AWS-pending run intentionally exits 2.

## Search behavior

- Per-incident lookback: default 30 days, ending exclusively at incident start.
- IP prevalence searches either endpoint across the supplied dataset.
- Activity recurrence requires the same directed source, destination, protocol
  and source site. It is not a behavioral/anomaly comparison.
- Country/company and optional domain/ASN/registered-organization searches are
  separate exact attribute matches, not evidence of the same activity.
- A negative answer requires complete declared history for the requested interval,
  supported fields and valid records. Otherwise the answer is unknown/unsupported.
- Original IDs, references, supplied labels, context status, zero/null values and
  extraction errors are preserved. Matching does not execute triage suggestions.

V3 omits the full domain/registration inventory. This consumer does not change or
relabel the producer schema. Supplemental context can explicitly provide those
attributes until a separately approved producer contract exposes them.

See [HISTORICAL_SEARCH.md](HISTORICAL_SEARCH.md) for exact schemas, matching rules,
limits and the AWS data-team checklist. [DESIGN.md](DESIGN.md) retains the original
broader enrichment proposal and is superseded for this historical-search build.

## Next integration milestone

Before packaging the AMS receiver after core changes:

```sh
python3 prepare_pod.py
python3 -m unittest discover -s tests -v
python3 prepare_pod.py --check
```

The implemented sequence is **Alert Triage → Enrichment → Recommendation**,
orchestrated by Triage's five stages. This receiver does not call other agents.
Downstream Donovan discovery tags are not required.

Get a redacted export/sample plus the data team's schema, partition layout,
coverage/watermarks, AWS region and IAM role requirements. Then implement the
adapter and test it against a limited authorized dataset. Partitioned Parquet
queried through Athena is a candidate architecture; it has not been selected or
implemented. S3 bucket availability alone is not enough to determine query logic.

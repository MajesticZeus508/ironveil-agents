# Hosted staging performance investigation

See the canonical [five-run evidence ledger](../triage_agent/STAGING_PERFORMANCE_2026-11-11.md).
Tests invoke the staging Network Investigation entry with the same seven-incident
synthetic dataset, not this receiver directly. No production changes are made.
All five parents and ten children are now reconciled platform-completed.

Initial three completed tests used Recommendation 0.1.4 and returned respectively
4/7, 6/7 and 5/7 validated analyses. Saved Markdown confirms five timeouts and one
validation rejection across those tests. Direct correlated seven-span client-call
means were 48.249s, 41.098s and 51.561s, versus 30.588s in the existing baseline.
All three maxima were approximately 90s, versus baseline 41.231s.

These are client-call spans, not isolated provider execution. Output incident
analysis_duration_seconds includes semaphore queue wait. Overlapping durations
must not be summed as run wall time. Trace metrics error_count=0 was observed in
a window with saved timeout failures, so metrics error counters are not treated
as evidence of successful inference. Platform completion is likewise distinct
from application analysis success. Upstream partial status is expected separately.

No causal attribution to provider capacity versus gateway queueing is established.
No timeout, concurrency, retry, model or prompt adjustment is implemented.

Final: success/failure counts 4/3, 6/1, 5/2, 7/0, 6/1; **28 of 35 analyses
succeeded**, six timed out and one failed validation. All five chains confirmed
five attachments and zero polling retries/errors. Recommendation active latency
min/median/max **137.260/163.427/184.144 seconds (n=5)**. Run 4 client-call mean/max
37.126/58.495s; run 5 43.701/90.044s. The original baseline active time was
116.606s with 7/7 analyses. One fully successful new run is insufficient for a
success-only latency distribution or SLA. Full per-incident JSON diagnostics are
not extracted because the API tool truncates large payloads; the ledger records
the exact saved JSON IDs for later full-byte retrieval without rerunning inference.

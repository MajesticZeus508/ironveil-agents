# Diagnostic release — 2026-11-18

Operator authorized publication and hosted write testing after reconnecting SGP.
AMS environment preflight ready=true: staging/platform. Each publish submitted
once; no retry of earlier unconfirmed file writes.

| Agent | Version | Agent ID | Source file |
|---|---|---|---|
| Enrichment | 0.1.5 | 420e63bd-8220-48bd-bada-743f0daea46c | c7a914e7-f679-4266-967e-f451bd5bf74a |
| Reporting | 0.1.9 | 934ba6f7-3dcc-4dfb-9454-acdc92f7a10f | 50a2c135-0e1c-4a79-a015-ead7e6a3bbc2 |
| Triage | 0.1.30 | d4ffbfc9-696f-4a5a-b174-75daaa1c993f | d93d02ff-4ae9-40c9-bb96-c3f0acc19e8d |

All three builder_check results ready=true, no blockers. Local Semgrep unavailable:
security scan unknown, not a clean scan attestation. Models/pins unchanged.
Triage release prepared with existing script, adjacent provenance; Dev IDs
unchanged, historical releases preserved. Re-ran nine write diagnostic tests:
9/9 passed against installed SDK 0.50.0; corrected an isolated-test import in
test code only (the complete 151-test prior run passed).

## Deployment and hosted result

All three versions active/latest, confirmed before one synthetic LUX chain
submission. Fresh complete SDK suites: **91 + 34 + 26 = 151 passed, no skips**;
Triage suite 422.087s. No source changes after the packaged owned runtime files.

- Parent: `inv_7ae33958-b73c-4260-a837-c63b3ba8cf6f`, thread
  `227c07f8-8041-4532-9704-2f7d6c5b89ec`, Triage **0.1.30**.
- Parent created 2026-11-18 **18:59:45.356433Z**, completed **19:00:45.596401Z**.
- Enrichment child: `inv_7169913e-64fc-4d80-8be0-c99f0abf3cc2`, version **0.1.5**,
  completed 19:00:06.188954Z.
- Reporting child: `inv_6b4b2937-7f9f-4305-8ad0-394a83f75a02`, version **0.1.9**,
  completed 19:00:44.429500Z.
- All five workflow stages completed; each child submitted exactly once.
  Seven original observations retained, unknown identity, unavailable AWS history,
  application partial; Reporting **1/1 analyses completed, zero failed**.

All three code-owned diagnostics agree:

```json
{
  "operation": "managed_file_write",
  "category": "missing_sgp_configuration",
  "http_status": null,
  "exception_type": "ValueError",
  "request_may_have_been_sent": false,
  "retry_policy": "never_automatically_retry"
}
```

Triage exposes it in `indicator_export.write_diagnostic`; both child collection
results expose the matching `export_diagnostics` after receipt verification.
This establishes missing/blank `SGP_API_URL` at the SDK URL-resolution boundary,
before write dispatch. No storage HTTP response exists for these attempts.
No confirmed file IDs/attachments, no file readback possible; remaining exports
stop as designed without retry. Generic final prose still says unconfirmed,
but the diagnostic removes request-sent ambiguity for this specific failure.

This is separate from the operator's now-healthy local SGP Teleport forward:
that forward serves bundle publication; deployed agents require platform-injected
runtime routing/configuration. Earlier API inspection also found no SGP policy
among the deployed policy pins. Platform owners should restore/verify SGP policy
attachment plus matching runtime URL injection, then test new sessions. We did
not hard-code a host, attach a lookalike policy, inject credentials, change platform
configuration, or retry writes. Storage availability after restoring configuration
is not yet established. The diagnostic proves the immediate cause, not why staging
lost the configuration or whether any further storage issue exists behind it.

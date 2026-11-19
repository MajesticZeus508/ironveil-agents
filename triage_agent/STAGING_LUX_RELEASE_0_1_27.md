# Staging detector compatibility release — 2026-11-16

Operator approved publication after local replay of all six rejected inputs.
Staging tenant: `6a1099f9e1ca37ee1216d8c3` (platform).

| Agent | Existing ID | Version | Source file ID |
|---|---|---|---|
| IronVeil Investigation — Start Here | d4ffbfc9-696f-4a5a-b174-75daaa1c993f | 0.1.27 | adbcdac2-d549-489d-ab2a-3d96f364aa41 |
| IronVeil Recommendations | 934ba6f7-3dcc-4dfb-9454-acdc92f7a10f | 0.1.6 | 59b3f5f9-765c-473d-8ce6-af0d6e14cef5 |

Both requests explicitly supply their existing display names and descriptions.
Enrichment and Events rules unchanged. No automatic replay or retry.

Triage prepared in `releases/staging_0_1_27/`; provenance outside deployable
directory records hashes and the three staging receiver-ID substitutions.
Prior release snapshots preserved. Empty production fixtures; pins unchanged.

Local CLI tests: 73 Triage (55 pass, 18 dependency skips), 20 Recommendation
(19 pass, one SDK skip). All six complete original captured inputs accept locally,
60 observations, zero input errors; unknown entity/metric semantics preserved.
See `LUX_COMPATIBILITY_2026_11_16.md` for exact scope and limitations.

The installed CLI did not resolve directory paths as pod agents and its export
attempt refused before upload. No host agent was exported/published. Instead the
reviewed runtime-only sources were packaged directly using the documented AMS
layout `agent/*.py` plus root `requirements.txt` and an empty package initializer.
No tests, reports, logs, credentials or input data were packaged. The clean archives
contain 18 Triage / seven Recommendation files. Syntax compiled before upload.
Local Semgrep unavailable; no local security-scan attestation.

Uploaded directly to SGP staging, then POSTed once each to the existing agents'
publish endpoints with explicit names, published lifecycle and model credential
injection. Source ZIP SHA-256:
- Triage: `1d09047631b25c834f6c76648429bb2baac43655aea2ce6dbd03974e0eec73c0`
- Recommendation: `f1d280bc67a810bc6cff76af91af842a0fc6c4ec56015e5dc394aa1361a56410`

Both publish requests accepted. Deployment observation in progress; acceptance
alone is not active deployment or hosted functional success.

Exact-version observation subsequently confirmed both versions **active/latest**.
Parent GETs confirmed **IronVeil Investigation — Start Here** and **IronVeil
Recommendations**, with versions 0.1.27 and 0.1.6 respectively.

## Hosted readiness blocker

Recommendation missing-input check `inv_a31eeca1-d021-4261-b4d0-2c9539137058`,
thread `8b349dcf-1709-4fba-b887-0472802cb06c`, failed **before application startup**.
The platform-provided startup traceback ends at Agent Kit Harness output
`configure_checkpointer` with:

`TypeError: Harness output requires JsonPlusSerializer or SparkJsonPlusSerializer; custom checkpoint serializers must integrate Harness event validation explicitly.`

This is a scaffold/checkpointer/SDK integration failure, not input rejection or
model inference. Container exited code 3 after two restarts. Do not call active
status functional acceptance. No serializer bypass, dependency-pin change or
automatic re-publication was attempted. Platform owners should check the current
deployed scaffold serializer against Agent Kit 0.50.0 Harness compatibility.
Recommendation deployment accepted/active does not prove successful graph compile.

Triage readiness submitted separately (no alert/file):
`inv_fa32f1be-e3e9-4feb-b30a-56901f53077c`, thread
`8a656480-099d-481c-a369-dfb8f25ac7e8`; outcome recorded below when available.

Triage likewise **failed before application startup with the identical Harness
serializer TypeError**, container exit 3 after two restarts. Both released versions
are active/latest administratively but **not functionally ready**. Escalate to MCPx
platform owners with the deployment versions, source IDs and invocation IDs above.
No received alerts were replayed; only two missing-input checks were submitted.

## Independent diagnosis recheck

Re-read both exact failed invocation records and exact-version metadata. Both
still report the same startup exception; administrative status remains active/latest.
Deployment IDs: Triage `e6a182b1-7730-4ae5-8398-f1cad0e8e754`, Recommendation
`cc149149-7cb8-465a-aaef-c59805cc5581`.

Inspected the locally installed **Agent Kit 0.50.0** source (not only current
repository main). `api_contracts/harness/output/contract.py:288-294` rejects when
the supplied saver serde is not `SparkJsonPlusSerializer` and either its exact
type is not `JsonPlusSerializer` or `_custom_unpack_ext_hook` is truthy.
Local dependency versions: langgraph 1.2.7, langgraph-checkpoint 4.1.1.
An isolated invocation of that contract method confirms:
- plain JsonPlusSerializer: accepted;
- JsonPlusSerializer subclass: exact deployed TypeError;
- JsonPlusSerializer with custom unpack hook: exact deployed TypeError;
- SparkJsonPlusSerializer: accepted.

No network, provider inference or checkpoint writes in that reproduction.
Uploaded archives contain only application modules/requirements and initializer;
no custom serializer, platform main.py, or spark_checkpointer.py. Requirements
retain the same 0.50.0 pin. Application changes concern parsing/prompt text, not
the checkpointer or graph compilation. Malformed archive/import would have failed
earlier; the traceback demonstrates imports reached graph compile.

**Attribution limit:** the bundled MCPx source's SparkCheckpointer declares plain
`JsonPlusSerializer()` and would pass this local check; its main.py line numbers
also differ from the live traceback. It is not authoritative for the exact
deployed image. Live SDK version is requested as 0.50.0 and traceback aligns with
local 0.50.0, but installed image distributions were not independently enumerated.
GitHub lookup of current MCPx source returned 404 under this account.

Thus the confirmed failure is the **Harness contract rejecting the runtime
checkpointer serializer during compile**. Specific serializer class, wrapper,
hook, package skew, and introducing change remain unverified. Ask MCPx owners for
`type(checkpointer.serde).__module__`, `.__qualname__`, whether its custom unpack
hook is set, installed SDK/checkpoint package versions, and scaffold revision for
these deployment IDs. Do not assert a proven platform regression or prescribe an
unverified upgrade. No new invocation, publish, rollback or validation bypass was
performed during this read-only/local reproduction recheck.

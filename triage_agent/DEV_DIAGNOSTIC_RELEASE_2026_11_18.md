# Dev diagnostic release — 2026-11-18

## Scope and verified target

Operator requested the latest three implementations on the existing Dev agents,
then exactly one synthetic LUX chain. `builder_env` verified active profile
`scalegov-dev`, tenant `69dfa4b844ff488d98b2674f`, Spark forward `mcpx-dev`,
and publication file forward `sgp-api-dev` before publication. All publish
responses independently reported that same profile and tenant.
No staging operation or platform-configuration change was performed. Existing
Dev display names were retained. No implementation or requirements changes.

| Existing name | Dev agent ID | Prior latest | Submitted version | Source bundle file ID | Local source |
|---|---|---|---|---|---|
| Network Investigation Demo | `7f244b84-ff27-43b0-a629-99a76791373a` | 0.1.25 | 0.1.30 | `70f5149a-6bd9-4dd3-9aec-025823e448d6` | `plugins/alert_triage/` |
| Historical Enrichment POC | `e8dc7ffc-c6d5-4920-9c12-a25e797835d8` | 0.1.2 | 0.1.5 | `ac7f2558-6581-408b-86e0-bf5f9fb1be55` | `../enrichment_agent/ams/` |
| Recommendation Agent POC | `2cf86942-3a14-40e4-95e5-4a90e752b259` | 0.1.3 | 0.1.9 | `2b34dedb-4ea4-42a2-8fdd-4e4589581013` | `../recommendation_agent/ams/` |

Triage editable `handoff.py` and `stages.py` were inspected: both target the Dev
receiver IDs above. Retained staging source was not used or modified. Each
publication was submitted once as published (not draft).

## Preflight evidence and limits

- All three `builder_check` results: ready=true, blockers=[]; local Semgrep absent,
  security scan unknown, not a clean-scan attestation.
- Enrichment `python3 prepare_pod.py --check`: `Pod core verified`.
- All three generic `builder_probe` runs imported/constructed the graphs but
  rejected messages-only input with required `task` / forbidden `messages`, before
  inference (gateway_calls=0). Strict Harness contracts were preserved; this is
  not a successful local functional acceptance run.
- Existing models retained. `openai/gpt-5.4` request-shape check: HTTP 200.
  `gemini/gemini-4-argon`: HTTP 429, provider TPM quota exhausted. No model fallback,
  quota workaround, or change to the approved implementation.
- Existing pins remain Agent Kit 0.50.0 / sling-agent 0.1.0.dev6. Fresh ordinary
  CLI regression: Triage 68 passed / 23 skipped (91 discovered), Enrichment 30
  passed / 4 skipped (34), Reporting 24 passed / 2 skipped (26). Total 122 passed,
  29 skipped, zero failures. SDK/httpx-dependent checks skipped; this is not
  equivalent to the earlier full-SDK staging suite.
- Verified the diagnostic interpretation against pinned `v0.50.0` source:
  `src/spark_agent_kit/middleware/resources/sgp_client.py` and `utils/http.py`.
  The public base URL resolver requires a usable SGP URL without a compiled
  fallback, before request dispatch. The [0.50.0 SGPResourceClient reference](https://scaleapi.github.io/spark-agent-kit/reference/platform/#spark_agent_kit.SGPResourceClient)
  says “there is no compiled fallback.” No dependency internals were modified.

The hosted input will use the complete preserved synthetic finding from
`tests/fixtures/lux_staging_2026_11_13.json`, unchanged, in one `lux_event` form,
retained as `DEV_LUX_INPUT_2026_11_18.json`.
The filename describes its provenance, not the deployment target. Seven evidence
rows, one finding/incident, unknown/null entity identity, opaque detector and
unknown measure are retained. This is a fresh Dev invocation, not a retry of
any earlier staging write, and not a live Events-rule test.

## Deployment and single-chain acceptance

AMS creation timestamps are **2026-11-19 UTC** (operator-local date Nov 18):
Enrichment `00:14:48.759064Z`, Triage `00:14:48.761305Z`, Reporting
`00:14:48.791681Z`. Deployment IDs:

- Triage: `b1f47c8c-cfaa-42b8-96e5-da82fda87160`.
- Enrichment: `075565d9-2a4c-4370-9d78-e2c81dfdcbd5`.
- Reporting: `7a8cbc47-9153-4271-8ee6-d9e35a8d5ec0`.

Read-only exact-version inspection reports no SGP policy among the six outbound
policy pins for any of these releases. This is configuration evidence, not yet
an observed file-write result. No policies or runtime settings were changed.

All three target versions confirmed active/latest before submission. Exactly one
fresh synthetic LUX chain submitted through `builder_invoke` (published/Harness):

- Parent invocation: `inv_811afc23-d1fa-4b70-9ddb-adcdb854ccbd`.
- Parent thread: `9defea86-47e0-45f6-96ee-f48a96beec46`.
- Initial observation: running after 45 seconds. Read-only reconciliation only;
  do not invoke again to poll, resume, or retry.

Parent created `2026-11-19T00:17:54.259898Z`, started `00:18:06.325154Z`.
Read-only child thread discovery and Enrichment output establish:

- Enrichment child `inv_d401f18f-50bd-4332-af8b-849c6acb1650`, thread
  `64e1c106-5f3d-49a6-9563-5c8805284efe`.
- Recommendation child `inv_243b1d54-e360-4908-82c8-cc6b32326f25`, thread
  `98ef3d8d-9e0b-4d68-87a0-fbba4dfa2d27`; initially running.
- Enrichment output: 23 prepared criteria, all `not_configured`, application
  partial, no actual historical searches. Structured result ready.
- Enrichment receipt: `alert-indicators/3`, structured, file_id=null,
  canonicalization=`canonical-json/1`, sha256=payload_sha256=
  `cf4081b27bca2a47fe86c7aaecc6a646a4082c6952ac46ab3e60b0036efca9d8`.
- Enrichment full structured payload SHA-256:
  `184eaeb7e116d8019257ac612b8fe102e8937b9faa4fac0dc4387710fca93814`.
- Enrichment's first export `enrichment_results.json` is unconfirmed; Markdown
  export stopped. No confirmed attachments in its action-scoped output. Diagnostic:

```json
{"operation":"managed_file_write","category":"missing_sgp_configuration","http_status":null,"exception_type":"ValueError","request_may_have_been_sent":false,"retry_policy":"never_automatically_retry"}
```

## Final reconciled result

**The managed-file issue persists in all three Dev agents.** All three return the
exact diagnostic above: missing/blank runtime SGP configuration, ValueError,
http_status=null, request_may_have_been_sent=false. No file upload was dispatched
by these attempts. The generic “file creation may have occurred” prose is broader
than the code-owned diagnostic and does not override its explicit false flag.

| Stage | Version | Platform result | Application/export result |
|---|---|---|---|
| Triage | 0.1.30 | completed | 1 finding, 1 group, 7 observations, zero input errors; extraction-only; `indicator_export.status=failed`, no attachment |
| Enrichment | 0.1.5 | completed | partial, 23 `not_configured` criteria; JSON unconfirmed; Markdown not attempted |
| Recommendation | 0.1.9 | completed | partial, 0/1 analyses completed, 1 failed (`model_request_failed`); JSON unconfirmed; Markdown not attempted |

The single parent completed `2026-11-19T00:20:06.945552Z`, **132.686 seconds**
after creation. Enrichment created `00:18:07.052858Z`, started `00:18:19.186031Z`,
completed `00:18:19.948063Z`. Recommendation created `00:18:21.860446Z`, started
`00:18:33.553976Z`; its thread reports completed/idle and final output updated
`00:20:04.538431Z` (output timestamp, not a claimed exact completion timestamp).

All five parent tool stages returned, both child submissions have `attempts=1`,
and both collectors report platform completed, application partial, exports=[].
Collection transient retries: zero (Enrichment 3 GET attempts; Recommendation 47).
Both canonical receipts were accepted by the parent's verification guards.
Recommendation receipt is `alert-enrichment/1`, structured, file_id=null,
canonicalization=`canonical-json/1`, sha256=payload_sha256=
`184eaeb7e116d8019257ac612b8fe102e8937b9faa4fac0dc4387710fca93814`.
LUX receipt SHA-256 is
`55442620a0c28275a512d0ba4b6cde99cd3b807bd34f8edf060ee5e189086480`
over 2,637 sorted compact UTF-8 event bytes (not transport-wrapper bytes).

**Confirmed attachments: zero; confirmed file IDs: none.** Triage's final answer
explicitly reports INVESTIGATION INCOMPLETE, 0/2 Enrichment files and 0/2
Recommendation files. No readback is possible without confirmed IDs. Source ZIP
upload IDs above are deployment bundles, not analyst-output attachments. An inline
Recommendation report discloses analysis unavailable, not a saved report or
successful analysis. The preflight Argon 429 is a separate observed quota issue;
the hosted sanitized `model_request_failed` alone does not prove its exact cause.

Parent lineage read links the invocation/thread and both Dev receiver agents;
no file nodes were returned (`truncated=false`). Child invocation IDs and parent
collection outputs, not lineage alone, establish the completed handoffs.

No resubmission, resume, model substitution, automatic write retry, hard-coded
endpoint, credential injection, custom-policy attachment or platform bypass.
Staging was not called or changed. Escalate the Dev runtime SGP URL/policy
configuration to platform owners with these agent/version/deployment/invocation
IDs. Storage health behind the missing configuration remains unknown; no
production conclusion is made. Any future acceptance is a separately approved
fresh run after platform repair, not a replay of uncertain writes.

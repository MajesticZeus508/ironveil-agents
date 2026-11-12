# Five-run staging benchmark — preflight blocked

> **Historical blocked checkpoint, subsequently resolved.** The operator's exact
> upload download is preserved as `staging_input_verification.json`, with matching
> SHA-256 and 62,315 bytes. The five authorized runs were subsequently completed;
> see [final evidence](STAGING_PERFORMANCE_2026-11-11.md). Do not launch five more
> runs by following the historical next-step text below.

No benchmark invocations were submitted. All five authorized runs remain unstarted.
No application, deployment, metadata, model or configuration changes were made.

## Environment and deployments

Live `builder_env` confirmed `scalegov-staging`, platform tenant
`6a1099f9e1ca37ee1216d8c3`. Live version checks returned:

| Agent | ID | Active/latest version |
|---|---|---|
| Entry | d4ffbfc9-696f-4a5a-b174-75daaa1c993f | 0.1.24 |
| Enrichment | 420e63bd-8220-48bd-bada-743f0daea46c | 0.1.3 |
| Recommendation | 934ba6f7-3dcc-4dfb-9454-acdc92f7a10f | 0.1.4 |

These status checks are not an independent image-security attestation.

## Input gate

Direct files-service metadata GET for staging file
`61827a37-3cb1-4a13-8445-cdf1e5ad8ded` returned HTTP 200:

- Filename: `ueba_findings_sim_run2_2026-11-03.json`
- Size: 62,315 bytes
- MIME: `application/json`
- Metadata checksum as returned: `eb39e52b1f56da07285de643738c9949`

The content GET also returned HTTP 200 and JSONL findings content, but the tool
truncated the response before exposing the full content. An independent SHA-256
of the downloaded staging bytes was therefore **not obtained**.

The existing local fixture, hashed read-only, returned:

- Size: 62,315 bytes
- SHA-256: `6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a`
- MD5: `3ceb08bcbfe68942e144a4d75a4ca510`

The local SHA-256 matches the requested value. However, the remote metadata
checksum does not equal the local MD5, so matching filename and size cannot
establish that the staging upload is byte-identical. This is a checksum-metadata
discrepancy, **not proof of a staging SHA-256 mismatch**. The metadata could be
incorrect; the full staging bytes must be independently hashed to decide.

The explicit requirement to verify the staging upload before inference is not
met. No local-file substitution or upload was performed. No timing samples,
statistics, completion rates, model traces or baseline performance comparison
are claimed for this requested five-run benchmark.

## Next step

Download this exact staging file through an approved full-byte download path and
compute its SHA-256, byte length and JSONL/extraction counts before proceeding.
Do not silently replace the upload. If it differs from the requested SHA-256,
stop and resolve the input identity with the operator. If it matches, continue
with exactly five new sequential runs and the original reconciliation/reporting
requirements. The existing staging baseline is not one of those five runs.

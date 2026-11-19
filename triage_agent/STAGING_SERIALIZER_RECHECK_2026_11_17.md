# Serializer readiness recheck / unchanged-source rebuild

Operator requested a fresh check and authorized redeployment if necessary.
ScaleGov staging / platform, tenant `6a1099f9e1ca37ee1216d8c3`.

Fresh missing-input invocations against existing releases both failed startup
with the same Harness serializer TypeError (no alert processing or inference):
- Triage 0.1.27: `inv_edcfd343-2e7d-4f5e-b6d8-c910b44908dc`,
  thread `0aedde42-76f9-43b1-bd56-26be3a49cf21`.
- Recommendation 0.1.6: `inv_1313bf00-8a0f-4ccb-9ac4-1d2dd905037c`,
  thread `3de4f6b7-1eec-483f-a84f-4879df6f50a3`.

Requested one unchanged-source rebuild per agent to test whether a current
platform fix must be incorporated at image construction. Reused exact existing
uploaded source IDs; no source upload, local code edit, dependency change,
serializer bypass, event replay, or automatic failed-submission retry.

| Display name retained explicitly | Version | Source ID | Deployment ID |
|---|---|---|---|
| IronVeil Investigation — Start Here | 0.1.28 | adbcdac2-d549-489d-ab2a-3d96f364aa41 | 991f5add-f394-41ae-a85d-910bfae668d4 |
| IronVeil Recommendations | 0.1.7 | 59b3f5f9-765c-473d-8ce6-af0d6e14cef5 | f27ff068-e813-471f-b60f-4db6f2ded056 |

Publication accepted; deployment and functional readiness are separate checks.
The SGP upload forward is down, but not required to reuse these stored bundles.
Triage's existing Donovan discovery tag/upload metadata retained in publish response.
No Enrichment or Events rule changes.

## Rebuild result — startup blocker cleared

Both new versions reached **active/latest** and freshly invoked successfully:
- Recommendation 0.1.7: `inv_0ce5466c-5896-4a48-ab7c-c96b01bfc2d5`, thread
  `28549514-6eec-4203-85b1-6df5300af740`, completed with expected
  `missing_enrichment` response, no stale input reused.
- Triage 0.1.28: `inv_59e25391-5e41-47cf-8a7a-59479f9a5140`, thread
  `2e56ca96-e98f-4fe0-888b-70dff6fbf6f9`, completed with expected missing-input
  message at run_triage, no analysis claimed.

Parent GETs verified exact original IronVeil names and unchanged source IDs.
New image digests:
- Triage: `sha256:72dd7e44ca97a3b5e6a70a849e8613d84ba28552e958cc3c0016996750c33a57`
- Recommendation: `sha256:d4e515afeeae878516a66d1d1bd248f42ad7cef9072acdbe52842cc95edbfbbc`

Evidence establishes that rebuilding unchanged application sources cleared the
observed serializer startup error. It does not identify the precise platform
change or installed transitive dependency difference. Full LUX input, downstream
file access, Enrichment startup and real inference remain a separate end-to-end
acceptance gate. No old alerts were replayed and no complete investigation is
claimed by missing-input readiness success.

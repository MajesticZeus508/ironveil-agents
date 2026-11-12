# Enrichment image security investigation — 2026-11-10 UTC

## Current outcome

**Superseding release checkpoint:** staging **0.1.3** is active/latest at live
housekeeping recheck. The operator-reported fix was followed by an unchanged-source
rebuild; recorded digest is
`sha256:a1dec129b99f0c3bb0c1b861b8f963ae32b42b088d92d6db8f75af649a0067dc`,
different from flagged 0.1.1/0.1.2. No final-image SBOM/fresh-scan proof was obtained.
See [release evidence](../triage_agent/STAGING_RELEASE_2026-11-10.md).
The inactive/same-digest investigation and prepared escalation below are historical,
not a claim that current 0.1.3 is inactive or uses that old digest.

## Historical 0.1.2 outcome and earlier investigation

Operator subsequently confirmed a complete successful run on Enrichment 0.1.2;
the AMS child record and parent receipts/attachments agree. Functional availability
is restored at this checkpoint, but **image remediation remains unverified**.
The operator supplied an engineer's Slack response identifying libexpat1 as a
staging-wide agent-base issue tracked in **PSP-3646**. This confirms platform
ownership; neither ticket status nor a fixed SBOM/fresh scan was independently
obtained. Triage 0.1.23 and Recommendation 0.1.3 are automatic rebuilds without
current compromise flags; that absence alone does not establish package versions.

**Later operator-requested retry:** 0.1.2 became active/latest on Nov 10 at
02:06:04Z, but reports the exact same image digest as vulnerable 0.1.1. No
verified patched build has been obtained. See `AMS_RELEASE.md` for release and
test IDs. The inactive-state statements below describe the earlier investigation.

**Blocked on platform image remediation/access; no fixed build obtained.**
Enrichment remains inactive after security takedown. Do not republish the same
bundle as a purported fix, waive the findings, restore the vulnerable image, or
disable scanning. No application source or deployment was changed in this
investigation.

Environment: ScaleGov staging; tenant `platform`
(`6a1099f9e1ca37ee1216d8c3`). Agent:
`420e63bd-8220-48bd-bada-743f0daea46c`.

## Confirmed live evidence

Exact-version GETs returned both versions inactive, compromised, and not latest:

| Version | Deployment | Image digest | Taken down (UTC) |
|---|---|---|---|
| 0.1.0 | `66ba5a01-76c8-443c-95ad-1062d2cb1846` | `sha256:0144edd52f8ce5631563bc7e7dc65348e481441d4b8015a523ca747c2d2cff53` | Nov 9 19:00:08.071751 |
| 0.1.1 | `79d1a1df-9e3a-4c62-b665-91f0d300cf4d` | `sha256:d14f490ea1555e76a100bf40e08ac235d3194e4da3e5928ab0406cf27111ef83` | Nov 10 00:00:06.313018 |

Both use source `957c7e7c-af75-4b38-bc6f-dafc077fc983` and both images
were subsequently deleted. Version 0.1.1 was built/deployed Nov 9 23:51–23:52,
but its findings still identify `libexpat1 2.9.0-r0`:

- CVE-2026-115506, HIGH; fixed in `2.10.0-r0`.
- CVE-2026-113351, MEDIUM; fixed in `2.10.0-r0`.

Different output digests do not prove different or patched OS layers.

The **live** `/openapi.json` explains:

- `AgentVersionResponse.base_image_status`: "Deprecated: base images are no
  longer a reason; ok for every vulnerability-based mark." Therefore `ok` is
  not a clean-image result.
- `CompromiseRebuildResponse.skip_reason=not_candidate`: "not an active,
  latest, source-built published version with an open finding no restore waived."
  This describes current eligibility, not why the vulnerable package was built
  or whether the rebuilder tried before takedown.

Read-only requests to `/v1/admin/base-image-rebuild/runs` and
`/v1/admin/compromised/versions` were denied. No tenant/identity changes or
alternate credential paths were attempted.

## Build mechanism and limits of the diagnosis

Bundled MCPx source HEAD `eec489c20cb1d0a7dd73b211e42bed2cabe612b0`
(2026-10-22) was inspected. It predates this incident and lacks the deployed
vulnerability/rebuilder implementation; it is not proof of the running worker's
exact code/configuration.

Relevant files under `mcpx-go/`:

- `internal/deployserver/activities/agent_build.go:27–35`: an unpinned agent
  inherits the configured golden base when available.
- `internal/deployserver/activities/dockerfile_template_agent.go:74–112`:
  golden builds add source and optional pip dependencies, not an OS upgrade.
- Same template, lines 17–42: standard builds inherit their agent/Python base
  and add build dependencies; there is no blanket OS upgrade.
- `internal/deployserver/activities/build.go:130–196`: neither ordinary Docker
  nor Buildx argument construction forces `--pull` or cache invalidation.
- `Dockerfile.agent-base:52–56`: parent is `python-fips:3.14-dev`; adding cairo
  does not establish that all inherited OS packages are updated.
- `Dockerfile.agent-golden-base:12–25`: inherits agent-base and installs the
  platform Python stack, with no blanket OS upgrade.
- `.github/workflows/build-push-agent-golden-base-image.yml:47–118`:
  golden base identity includes the resolved immutable agent-base digest;
  rerunning against the same inputs can retain the existing artifact.
- `internal/deployserver/activities/agent_build.go:282–288`: MCPx overwrites
  user Dockerfiles with its managed template. Adding a pod Dockerfile is not
  a reliable fix.

These mechanisms explain how a new agent image can preserve an old OS package.
**Not established:** which configured base/digest 0.1.1 actually used, whether
the stale package came from that base or an added native layer, whether a newer
base is already available in GovCloud, or whether cache/pull behavior caused
the stale selection. Those require current build logs/provenance and SBOMs.

## Ready-to-send escalation to #mcpx

> Enrichment is repeatedly security-disabled in ScaleGov staging/platform.
> Agent `420e63bd-8220-48bd-bada-743f0daea46c`, version 0.1.1,
> deployment `79d1a1df-9e3a-4c62-b665-91f0d300cf4d`, image digest
> `sha256:d14f490ea1555e76a100bf40e08ac235d3194e4da3e5928ab0406cf27111ef83`.
> A fresh source republish still contains libexpat1 2.9.0-r0; Trivy findings
> CVE-2026-115506 HIGH / CVE-2026-113351 MEDIUM require 2.10.0-r0.
> Marked 2026-11-10 00:00:03Z, taken down 00:00:06Z, image deleted 00:00:10Z.
> Please inspect the build's resolved agent/golden base digest, native-package
> layers and SBOM, rebuild the affected base chain from patched OS packages,
> replicate it to staging's registry, and ensure the build worker selects that
> exact patched digest rather than a cached predecessor. Please provide the
> resulting base/image digest and package/scan evidence. Our admin rebuild and
> compromised-version reads are denied. Do not waive or restore the vulnerable
> image; we need a genuinely patched build, not a security exception.

This message is prepared locally; it has **not** been sent to a support channel.

## Completion gates after platform remediation

1. Confirm the build input's SBOM/package inventory has fixed libexpat1
   `2.10.0-r0` (or an explicitly verified fixed successor for the same distro).
2. Publish a new version of the existing agent with unchanged application
   behavior; record source ID, resolved base and final image digest.
3. Require a completed vulnerability scan of the final image: no open findings
   for these CVEs. Initial `compromised=false` before scan ingestion is not proof.
4. Confirm active/latest after the security sweep, then run isolated strict
   Harness file acceptance and the full investigation chain.
5. Preserve `not_configured` history, partial status, receipts and human review.

Previous successful invocations prove application behavior only during those
windows; they do not supersede the subsequent security takedown.

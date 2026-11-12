# AMS staging inventory and local preservation

## Scope and completeness

Read-only live inventory: **scalegov-staging / platform**,
tenant `6a1099f9e1ca37ee1216d8c3`. `GET /v1/agents` returned **seven agents**.
This covers agents visible to the connected identity in this tenant—not every
tenant, all account files, runtime filesystems, secrets or platform infrastructure.

**The requested complete local mirror is not yet achieved.** All three network
implementations are present, but two older operator-owned VoF agents are absent.
Current source bundles have not been freshly downloaded/byte-compared. Hosted
evaluation reports are largely represented by retained IDs/ledgers, not local files.
Platform defaults are inventoried, not silently recreated as project agents.

## Live agent inventory

The three IronVeil staging display names/descriptions were updated and reread on
2026-11-12. IDs, active versions, source references and discovery metadata were
unchanged. Other inventory rows below retain the earlier housekeeping checkpoint.
Historical records retain the former Demo/POC names.

| Agent | AMS ID | Live state / version | Local coverage |
|---|---|---|---|
| **IronVeil Investigation — Start Here** | `d4ffbfc9-696f-4a5a-b174-75daaa1c993f` | active/latest **0.1.24** | Entry point, orchestration and triage; prepared staging release and provenance in `triage_agent/releases/`; historical downloaded 0.1.17 snapshot |
| IronVeil Historical Enrichment | `420e63bd-8220-48bd-bada-743f0daea46c` | active/latest **0.1.3** | Supporting agent; `enrichment_agent/ams/`; root core freshness passed; no downloaded current snapshot |
| IronVeil Recommendations | `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f` | active/latest **0.1.4** | Supporting agent; `recommendation_agent/ams/`; no downloaded current snapshot |
| VoF CTI Hunt Package | `fff45061-e9ac-43bf-973d-6024640db353` | inactive; highest listed **0.1.5**, not latest | **Missing source locally**; 0.1.3–0.1.5 share retained source ID below |
| VoF IR Notables Review | `21865c96-2deb-41dc-b5c0-68ba826c55cc` | inactive; highest listed **0.1.8**, not latest | **Missing source locally**; 0.1.5–0.1.8 share retained source ID below |
| Chat Agent (platform default) | `f45b29ad-06d0-4207-a9f7-318fe83697fb` | active **1.0.0** | Platform-owned; source not mirrored locally |
| Donovan Chat (platform default) | `8b8771fa-c4d4-4927-8c59-7df859e3888f` | inactive; no version/source in listing | Metadata inventory only; no recoverable source established |

All seven listing records reported `compromised=false`, `takedown_at=null`.
These are point-in-time fields, not vulnerability-scan attestations. Inactive VoF
versions have historical takedown/image-deletion records; no reason is inferred
from the absence of a current compromise flag.

## Retained source bundles

| Agent/version | SGP source file ID | Metadata read |
|---|---|---|
| Entry 0.1.24 | `b06c9ba3-3223-4bdb-8281-61fba2bab92e` | Content GET 200, but tool decoded ZIP as lossy text; **not saved** |
| Enrichment 0.1.3 | `2eb071f0-fe65-4d6f-a477-17819787f720` | 200; 15,600 bytes; MD5 `6fda30a9ce2eb6eac8b16868ce3fd0a9` |
| Recommendation 0.1.4 | `eb82adf2-8f84-4008-9da8-48bdbe6b929b` | 200; 16,177 bytes; MD5 `05032e40adc741ec6b6aa5c32d9d8ed0` |
| VoF CTI 0.1.5 | `579682b7-9518-4ab8-a4fd-f16820e438cd` | 200; 17,818 bytes; MD5 `00ea6e2cf025fe79ec1d01b46f525a76` |
| VoF IR 0.1.8 | `04e2b5b4-ea54-4be5-8708-3ea70cf47c8a` | 200; 20,231 bytes; MD5 `30a43a7f766091abf6075160efeef09a` |
| Default Chat 1.0.0 | `dff9baf8-21e4-4f39-9d1b-42925a2b2b8c` | Source ID from listing; content availability not checked |

MD5 values are API metadata, not independently calculated local integrity proof.
No lossy tool response was reconstructed into a ZIP. No credentials, environment
values or signed URLs were exported. No agent was republished or restored.

## Local source distinction

- `triage_agent/plugins/alert_triage/` targets **Dev** receiver IDs.
- `triage_agent/releases/staging_0_1_24/` is the isolated staging source; associated
  `.provenance.json` records file hashes and the three receiver-ID replacements.
- `triage_agent/ams_snapshots/0.1.17/` is an older downloaded source snapshot,
  preserved unchanged. Its historical byte equality does not apply to today's code.
- Enrichment owns root `contracts.py`, `enrich.py`, `history.py`; staged `ams/`
  copies passed `prepare_pod.py --check`.
- Recommendation implementation is owned directly in `recommendation_agent/ams/`.

## Recovery handoff — operator action required

The available builder API tool has no binary-save destination. Its ZIP content
response is text-decoded/truncated, so it cannot establish exact source recovery.
Use the supported binary-safe pull path from the project root with AMS connected
to **scalegov-staging**. Never overwrite editable source or add `--force`:

```sh
sling ams pull d4ffbfc9-696f-4a5a-b174-75daaa1c993f --version 0.1.24 -o ./triage_agent/ams_snapshots/0.1.24/alert_triage
sling ams pull 420e63bd-8220-48bd-bada-743f0daea46c --version 0.1.3 -o ./enrichment_agent/ams_snapshots/0.1.3/ams
sling ams pull 934ba6f7-3dcc-4dfb-9454-acdc92f7a10f --version 0.1.4 -o ./recommendation_agent/ams_snapshots/0.1.4/ams
sling ams pull fff45061-e9ac-43bf-973d-6024640db353 --version 0.1.5 -o ./vof_cti_hunt_package/ams_snapshots/0.1.5
sling ams pull 21865c96-2deb-41dc-b5c0-68ba826c55cc --version 0.1.8 -o ./vof_ir_notables_review/ams_snapshots/0.1.8
```

Exact-version pulls for inactive agents must be confirmed supported/access-permitted;
if refused, recover the listed retained source ZIP through AMS Files download.
After recovery, safely inspect archive paths, preserve original bytes and calculate
SHA-256 per file; compare against the correct local staging tree. Do not register
recovered snapshots as runnable plugins or assume they are safe to execute.

The platform-default Chat source, older distinct-version bundles and historical
drafts need separate preservation if “everything” includes platform-owned/history
rather than current project source. No claim of those backups is made.

## Evaluation/output recovery

The [five-run ledger](triage_agent/STAGING_PERFORMANCE_2026-11-11.md) records all
25 confirmed file IDs. Download original Triage, Enrichment and Recommendation
files into agent-scoped, per-run output directories; retain file ID/byte size/hash
receipts outside deployable source. Do not regenerate reports or rerun inference
to replace missing evidence. The original input is already local as
`triage_agent/staging_input_verification.json`, hash-verified at cleanup.

# LUX payload compatibility — local candidate

No publication, hotswap, rule change, live invocation, or receiver edit performed.
Existing release snapshots and existing uncommitted integration work preserved.

## Evidence reviewed before selecting rules

- `LUX_EVENT_INGESTION_PLAN.md`, `LUX_EVENT_INGESTION_IMPLEMENTATION.md`,
  `LUX_Alert.md`, scoped instructions, README and shared DEMO runbook.
- Earlier operator-supplied Events Log finding `a2cc03ec-df67-475a-900d-de116e178838`:
  explicit host/site, `egress_volume_hourly`, explicit hourly measure, 12 reported
  destinations and ten evidence rows. Existing exact-pair handling remains.
- Latest stored staging invocation `inv_f898ec01-08ee-42c8-a2f0-6a779cb86f2e`,
  thread `7a5035ec-58d7-40a4-8060-a4dd85bd54b8`, version **0.1.25**, created
  `2026-11-13T19:22:35.789983Z`: structured `lux_event` form arrived intact.
  Its output records `no_valid_findings` / `unsupported entity`, zero exports.
  Finding `53e709b3-388f-4fc2-ac4f-ed09bbec912c` has
  `{type: "unknown", id: null, site: null}`, detector `to AMS egress_volume`,
  measures `unknown`, observed 7, seven evidence rows, and placeholder incident key
  `unknown:None@2026-11-13T15:15:00.000Z`.
- The two preceding readable stored invocations were no-input readiness checks,
  not additional LUX findings. Thus only two actual payload shapes were reviewed;
  no claim that all current LUX detector variants are covered.

The operator identifies Spark event `39594a0b-f3dd-478e-9567-b20d5961acbd`.
That ID is absent from the submitted form and output receipt. An Events service
base was not configured in this shell; the event/action record was not fetched,
and the event-to-invocation link is operator-reported, not independently verified.
No delivery ID was invented or inserted into the fixture.

Captured decoded finding: `tests/fixtures/lux_staging_2026_11_13.json`.
Canonical UTF-8 serialization SHA-256 matches the hosted receipt exactly:
`55442620a0c28275a512d0ba4b6cde99cd3b807bd34f8edf060ee5e189086480`.
This is decoded-object preservation, not a claim about original transport bytes.
Fixture is synthetic and test-only; not bundled into production `fixture/`.

## Explicit compatibility rules

1. Existing schema, size, record, evidence, numeric, timestamp and deduplication
   validation stays in force. File/event inputs use the same deterministic parser.
2. For source `swoop/valhalla/simulated`, permit exactly the observed unresolved
   entity object with keys `type`, `id`, `site`, values `unknown`, null, null.
   A null whole entity, null ID on a host, other unknown shapes and arbitrary new
   entity types still fail. Preserve supplied object and incident key unchanged.
3. The same source may supply exactly `to AMS egress_volume` / `unknown` as an
   **opaque** detector/measure pair. No prefix stripping, fuzzy matching, alias,
   default units, threshold or detector interpretation. Other unsupported pairs
   still fail. All original metrics remain in full deterministic results.
4. Add `unknown_entity` and `unknown_measure_semantics` quality issues. The latter
   carries original detector, measures, observed, baseline and scores through the
   existing v3 incident quality-issue field. No schema version or new top-level
   handoff fields. Known canonical pairs retain their original semantics.
5. **No evidence-to-identity inference rule is enabled.** Even unanimous evidence
   `src`/`src_site` values remain source/site observations, not entity identity.
   Unknown findings are isolated by finding ID after normal ID deduplication;
   the placeholder incident key cannot merge distinct unresolved entities.
6. Optional Triage narrative prompts explicitly forbid identity filling and
   interpretation of the opaque pair. Prompt wording is not semantic proof.

Extraction may be completed with quality warnings; this is not resolved identity
or a complete investigation. Default narrative remains deferred. No retries,
external sources, AWS access, write-back or response actions added.

## Downstream release gate

**Subsequent authorized local follow-up:** Recommendation now accepts this exact
synthetic unknown/null entity shape and preserves it with explicit report warnings;
see [receiver verification](../recommendation_agent/VERIFICATION.md#lux-compatibility-follow-up--2026-11-13).
Real local Triage → unconfigured-history Enrichment → stub Recommendation/export
compatibility passes. Managed suites: 72 Triage + 19 Recommendation, zero skips.
Nothing published. The incompatibility described below is the original inspection
finding, resolved in editable source only; hosted release/acceptance still pending.

The current Enrichment `validate_handoff` accepts an entity object containing
unknown/null identity and the unmodified v3 quality issues. The current
Recommendation `ams/core.py:validate` requires a nonempty `entity.id` and type
host/external_service/site. It will reject this handoff (`invalid_text`) before
inference. A local regression asserts this incompatibility explicitly.

**Do not publish this as full-chain acceptance.** Recommendation needs a separately
approved unknown-identity contract/prompt/renderer change and tests before an
end-to-end release. No receiver source was changed and no fake host was substituted
to bypass its validator. Existing stage failure handling preserves prior exports.

## Verification

- Plain CLI: 72 tests, 54 passed / 18 SDK-httpx skips, zero failures (before the
  managed follow-up; managed run includes final test assertions).
- Managed local `builder_probe(triage_agent/tests/reliability_verify)`:
  **72 Triage tests + 15 Recommendation tests passed, zero skips**;
  reply `SDK tests and five-stage checkpoint workflow passed`.
  Triage suite 142.887s; Recommendation suite 0.064s.
- Captured payload: one accepted finding, one isolated incident, seven exported
  observations; exact original metrics/entity retained; file/event export parity.
  Legacy fixture remains 17 findings / seven groups / 98 observations.
- Checkpoint workflow test now uses the captured unknown-entity payload and checks
  quality flags, all five stages under **stubbed** resource/downstream services,
  receipt propagation, thread isolation and uncertain-collection stop behavior.
  Stubbed downstream success does not establish real receiver compatibility.
- Managed probe reported 12 gateway calls, zero refusals; not an offline-only or
  inference-free test. Runtime was the managed pinned 0.50.0 environment; no SDK
  API changes or dependency pin changes were made. Existing future checkpoint
  serializer registration warning remains; no SDK internals were patched.
- `builder_check(triage_agent/plugins/alert_triage)`: **ready=true**, zero blockers;
  Semgrep unavailable, scan **unknown**, not clean.

Approval gates: broader representative Events payload review if additional shapes
are required, Recommendation compatibility authorization, deploy/security checks,
then approved staging publication and real event-path acceptance. No publication
is authorized by these local results.

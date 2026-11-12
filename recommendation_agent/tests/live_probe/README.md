# Local-only managed diagnostic — never publish

This scaffold is a development runner, not Recommendation Agent production source.
It imports the actual implementation from `../../ams/` and synthetic Enrichment
examples from `../../../enrichment_agent/outputs/`. It is not self-contained.

Running it through the managed `builder_probe`:

1. Runs the 14-test suite in the SDK runtime.
2. Calls the actual production graph with a text-only Harness request to check
   the missing-file path (no real managed attachment read/write).
3. Makes **two real Argon calls**, one complete synthetic-history example and one
   AWS-pending example, and saves new timestamped directories in `../../outputs/`.

Use the full directory path for builder_probe; the local plugin name is not in a
scan root. Do not substitute this runner for the production publish target or
loosen the production input schema for the messages-only generic probe.

It incurs model usage and writes new local evidence. Do not run merely for docs,
and do not present a completed runner as proof that every narrative validated:
inspect each returned run's completed/failed counts. Historical results and exact
limits are in `../../VERIFICATION.md`.

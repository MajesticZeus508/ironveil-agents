# Recommendation Agent

Start with README.md, CONTRACT.md and VERIFICATION.md. Current checkpoint is
Recommendation Agent POC 0.1.4 (unchanged-source rebuild of concurrency-two implementation),
agent 934ba6f7-3dcc-4dfb-9454-acdc92f7a10f,
ScaleGov staging / platform. Recheck state rather than assuming it remains latest.

Keep this agent separate; do not modify Triage, Enrichment or release snapshots.
The Triage entry already invokes this receiver automatically; this receiver does
not invoke other agents. Only the entry needs the Donovan discovery tag.
Input is alert-enrichment/1 with embedded alert-indicators/3. Preserve provenance,
partial status, search coverage and synthetic flags. No AWS, intelligence lookups,
agent invocation, shell tools or autonomous response actions are authorized.
Argon supplies cybersecurity interpretation and proposed actions, never new facts.
All disruptive recommendations require explicit conditions and human approval.
Core source is in ams/; tests and example outputs stay outside the pod.
Never bundle received handoffs or examples in ams/fixture/.
Never hand-edit scaffold requirements or persist provider exception text/secrets.
Run python3 -m unittest discover -s tests -v from this directory.

No staging script: edit the owned implementation directly in ams/. recommend.py
imports that implementation. Model/prompt configuration also lives in core.py;
changing graph.py alone does not change the incident-analysis model/prompt.
Publish only ams/, never the parent directory or tests/live_probe/.
The diagnostic runner makes real model calls and creates new output directories;
do not run it for documentation-only housekeeping. Plain CLI skips one SDK test.
Never loosen the Harness input contract to fit the generic messages-only probe.
Preserve historical outputs; outputs/README.md distinguishes failures and successes.
Do not silently overwrite/regenerate examples with a newer renderer.
Release, hotswap, discovery tags and automatic integration need explicit operator
authorization. Housekeeping does not imply a publish or Git commit.

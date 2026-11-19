"""One explicit hosted synthetic invocation; durable IDs before read-only wait."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from sling.settings.secrets import load_into_env
from sling.config import load
from sling.ams import Client, profile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("enrichment", "recommendation", "triage"))
    parser.add_argument("--label", default="", help="Unique evidence suffix for an explicitly requested fresh test")
    args = parser.parse_args()
    destinations = {"enrichment": ("420e63bd-8220-48bd-bada-743f0daea46c", "0.1.4"),
                    "recommendation": ("934ba6f7-3dcc-4dfb-9454-acdc92f7a10f", "0.1.8"),
                    "triage": ("d4ffbfc9-696f-4a5a-b174-75daaa1c993f", "0.1.29")}
    agent, version = destinations[args.target]
    if any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in args.label):
        raise ValueError("invalid_evidence_label")
    suffix = "_" + args.label if args.label else ""
    path = ROOT / f"HOSTED_STRUCTURED_{args.target}_{version}{suffix}.json"
    if path.exists(): raise ValueError("existing_invocation_reconcile_do_not_resubmit")
    if args.target == "triage":
        event = json.loads((ROOT / "tests/fixtures/lux_staging_2026_11_13.json").read_bytes())
        part = {"type": "form", "slot": "lux_event", "params": {"event": event}}
    else:
        data = json.loads((ROOT.parent / "enrichment_agent/fixtures/triage_v3.json").read_bytes())
        if args.target == "recommendation":
            from enrichment_agent.enrich import enrich
            from enrichment_agent.history import UnconfiguredAWSHistory
            data = enrich(data, UnconfiguredAWSHistory())
        part = {"type": "form", "slot": "triage_handoff" if args.target == "enrichment" else "enrichment_handoff",
                "params": {"handoff" if args.target == "enrichment" else "enrichment": data}}
    value = {"task": {"intent": "dispatch", "payload": {"parts": [part]}}}
    load_into_env()
    cfg = load()
    with Client(profile("scalegov-staging", cfg.ams.profiles), "6a1099f9e1ca37ee1216d8c3") as client:
        record = client.request("GET", "agents", f"/v1/agents/{agent}")["body"]
        if record.get("version") != version or record.get("status") != "active":
            raise ValueError("expected_version_not_active")
        evidence = {"agent_id": agent, "version": version, "status": "submission_uncertain"}
        def save(): path.write_text(json.dumps(evidence, indent=2) + "\n")
        save()
        started = client.invoke(agent, input=value, contract="harness", version_type="published")
        evidence.update(started=started)
        save()
        print(json.dumps(started), flush=True)
        terminal = client.await_invocation(started["invocation_id"], timeout=1000,
                                           on_state=lambda s: print(s, flush=True))
        evidence["terminal"] = {k: terminal.get(k) for k in ("status", "failure_code", "failure_phase", "version")}
        evidence["status"] = terminal.get("status")
        save()
        if terminal.get("status") != "completed": return
        output = client.invocation_output(started["invocation_id"])
        evidence["output"] = output
        save()
        print("stored output retrieved", flush=True)


if __name__ == "__main__": main()

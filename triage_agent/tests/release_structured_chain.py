"""Operator-authorized staging release; one upload/publish per selected agent.

Run with Slingshot's installed Python. Uses its existing secure secret store;
never prints credentials or retries additive operations. Local-only, not bundled.
"""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from sling.settings.secrets import load_into_env
from sling.config import load
from sling.ams import Client, profile
from sling.bundle import AgentSpec, pack_pod
from sling.scan import scanner

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {
    "enrichment": ("enrichment_agent/ams", "420e63bd-8220-48bd-bada-743f0daea46c", "0.1.4"),
    "recommendation": ("recommendation_agent/ams", "934ba6f7-3dcc-4dfb-9454-acdc92f7a10f", "0.1.8"),
    "triage": ("triage_agent/releases/staging_0_1_29", "d4ffbfc9-696f-4a5a-b174-75daaa1c993f", "0.1.29"),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=TARGETS)
    args = parser.parse_args()
    path, agent_id, version = TARGETS[args.target]
    evidence = ROOT / "triage_agent" / f"STRUCTURED_RELEASE_{args.target}_{version}.json"
    if evidence.exists():
        raise ValueError("existing_release_evidence_reconcile_before_any_new_submission")
    load_into_env()
    cfg = load()
    selected = replace(profile("scalegov-staging", cfg.ams.profiles), files_url="http://127.0.0.1:18085")
    bundle = pack_pod(AgentSpec(name=args.target, kind="pod", graph="graph"),
                      plugin_dir=ROOT / path, scanner=scanner())
    archive = bundle.to_zip()
    print(bundle.report, flush=True)
    record = {"agent_id": agent_id, "version": version, "path": path,
              "archive_sha256": hashlib.sha256(archive).hexdigest(),
              "created_at": datetime.now(timezone.utc).isoformat(), "status": "prepared",
              "files": {k: hashlib.sha256(v).hexdigest() for k, v in bundle.files.items()}}
    def save():
        evidence.write_text(json.dumps(record, indent=2) + "\n")
    with Client(selected, "6a1099f9e1ca37ee1216d8c3") as client:
        current = client.request("GET", "agents", f"/v1/agents/{agent_id}")["body"]
        if any(v.get("version") == version for v in client.versions(agent_id)):
            raise ValueError("version_exists_reconcile")
        record.update(display_name=current["display_name"], previous_version=current.get("version"))
        save()  # Durable intent before additive upload.
        record["status"] = "upload_uncertain"
        save()
        record["file_id"] = client.upload_source(archive)
        record["status"] = "uploaded"
        save()
        record["status"] = "publish_uncertain"
        save()
        response = client.publish_version(agent_id, display_name=current["display_name"],
            description=current.get("description", ""), version=version, file_id=record["file_id"],
            metadata=current.get("metadata", {}))
        record.update(status="publication_accepted", response=response)
        save()
        print(json.dumps({k: record[k] for k in ("agent_id", "version", "file_id", "status")}), flush=True)


if __name__ == "__main__":
    main()

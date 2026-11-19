"""Explicit operator-requested retry; reuse uploaded sources, never auto-retry."""
from datetime import datetime, timezone
import json
from pathlib import Path
from sling.settings.secrets import load_into_env
from sling.config import load
from sling.ams import Client, profile, AmsError

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_into_env()
    cfg = load()
    with Client(profile("scalegov-staging", cfg.ams.profiles), "6a1099f9e1ca37ee1216d8c3") as client:
        for target, version in (("enrichment", "0.1.4"), ("recommendation", "0.1.8")):
            path = ROOT / f"STRUCTURED_RELEASE_{target}_{version}.json"
            record = json.loads(path.read_text())
            agent_id = record["agent_id"]
            if any(v.get("version") == version for v in client.versions(agent_id)):
                print(target, "version already exists; reconcile without publishing", flush=True)
                continue
            current = client.request("GET", "agents", f"/v1/agents/{agent_id}")["body"]
            attempt = {"requested_at": datetime.now(timezone.utc).isoformat(),
                       "status": "publish_uncertain", "source_file_id": record["file_id"]}
            record.setdefault("operator_requested_retries", []).append(attempt)
            def save(): path.write_text(json.dumps(record, indent=2) + "\n")
            save()
            try:
                response = client.publish_version(agent_id, display_name=current["display_name"],
                    description=current.get("description", ""), version=version,
                    file_id=record["file_id"], metadata=current.get("metadata", {}))
                attempt.update(status="publication_accepted", response=response)
                print(target, "publication accepted", flush=True)
            except AmsError as exc:
                # Retain only the known fixed platform failure, no arbitrary body.
                known = "Authentication dependency unavailable" in str(exc)
                attempt.update(status="failed_platform_dependency" if known else "failed_or_uncertain",
                               error="ARP 503 Authentication dependency unavailable" if known else "publish_failed_reconcile")
                print(target, attempt["error"], flush=True)
            finally:
                save()
            versions = client.versions(agent_id)
            attempt["version_observed_after_request"] = any(v.get("version") == version for v in versions)
            save()
            print(target, "new version observed:", attempt["version_observed_after_request"], flush=True)


if __name__ == "__main__":
    main()

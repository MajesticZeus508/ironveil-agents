"""Prepare an isolated staging release without editing the Dev working pod.

Run from triage_agent with an explicitly new destination under that directory.
Only downstream receiver IDs differ; scaffold requirements are copied unchanged.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "plugins" / "alert_triage"
REPLACEMENTS = {
    "handoff.py": {
        "e8dc7ffc-c6d5-4920-9c12-a25e797835d8": ("420e63bd-8220-48bd-bada-743f0daea46c", 1),
        "2cf86942-3a14-40e4-95e5-4a90e752b259": ("934ba6f7-3dcc-4dfb-9454-acdc92f7a10f", 1),
    },
    "stages.py": {"2cf86942-3a14-40e4-95e5-4a90e752b259": ("934ba6f7-3dcc-4dfb-9454-acdc92f7a10f", 1)},
}


def prepare(destination):
    destination = destination.resolve()
    if not destination.is_relative_to(ROOT) or destination.exists():
        raise ValueError("destination_must_be_new_and_agent_scoped")
    if any((SOURCE / "fixture").iterdir()):
        raise ValueError("review_nonempty_production_fixture_first")
    files = sorted([*SOURCE.glob("*.py"), SOURCE / "manifest.json", SOURCE / "requirements.txt"])
    prepared, hashes = {}, {}
    for source in files:
        raw = source.read_bytes()
        changed = raw
        for old, (new, count) in REPLACEMENTS.get(source.name, {}).items():
            if changed.count(old.encode()) != count:
                raise ValueError("receiver_replacement_count_changed")
            changed = changed.replace(old.encode(), new.encode())
        if source.suffix == ".py":
            compile(changed, source.name, "exec")
        prepared[source.name] = changed
        hashes[source.name] = {"source_sha256": hashlib.sha256(raw).hexdigest(),
                               "release_sha256": hashlib.sha256(changed).hexdigest()}
    destination.mkdir(parents=True)
    (destination / "fixture").mkdir()
    for source in files:
        if source.name in REPLACEMENTS:
            (destination / source.name).write_bytes(prepared[source.name])
        else:
            shutil.copyfile(source, destination / source.name)
        if (destination / source.name).read_bytes() != prepared[source.name]:
            raise ValueError("release_copy_mismatch")
    # Keep provenance OUTSIDE the deployable pod.
    destination.with_suffix(".provenance.json").write_text(json.dumps({
        "source": str(SOURCE.relative_to(ROOT)), "target_environment": "scalegov-staging",
        "tenant_id": "6a1099f9e1ca37ee1216d8c3", "files": hashes,
    }, indent=2) + "\n")
    print(f"Prepared {len(files)} files; only three receiver ID occurrences changed; Dev source untouched.")


if __name__ == "__main__":
    prepare(Path(sys.argv[1]))

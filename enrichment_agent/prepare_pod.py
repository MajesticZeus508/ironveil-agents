"""Stage owned core modules into the isolated pod; no dependencies or secrets."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ("contracts.py", "enrich.py", "history.py")


def prepare(check=False):
    hashes = {}
    for name in FILES:
        content = (ROOT / name).read_bytes()
        hashes[name] = hashlib.sha256(content).hexdigest()
        target = ROOT / "ams" / name
        if check:
            if not target.exists() or target.read_bytes() != content:
                raise ValueError("Stale pod core: " + name)
        else:
            target.write_bytes(content)
    manifest = json.dumps({"source": "enrichment_agent core", "sha256": hashes}, indent=2) + "\n"
    path = ROOT / "ams" / "core_provenance.json"
    if check:
        if not path.exists() or path.read_text() != manifest:
            raise ValueError("Stale core provenance")
    else:
        path.write_text(manifest)
    return hashes


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    prepare(check=args.check)
    print("Pod core verified" if args.check else "Pod core staged")

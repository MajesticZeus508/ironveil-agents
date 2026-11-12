"""Read-only Markdown checks; excludes immutable output and source snapshots."""
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]


def main():
    documents = list(ROOT.glob("*.md"))
    for name in ("triage_agent", "enrichment_agent", "recommendation_agent"):
        documents.extend((ROOT / name).glob("*.md"))
    documents.append(ROOT / "recommendation_agent/outputs/README.md")
    errors = []
    for path in sorted(set(documents)):
        fence = None
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = re.match(r"^\s*(`{3,}|~{3,})", line)
            if match:
                marker = match.group(1)
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
            if fence is not None:
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", line):
                target = target.split("#", 1)[0]
                if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                if not (path.parent / unquote(target)).exists():
                    errors.append(f"{path.relative_to(ROOT)}:{number}: missing {target}")
        if fence:
            errors.append(f"{path.relative_to(ROOT)}: unclosed fence")
    for error in errors:
        print(error)
    print(f"Checked {len(set(documents))} Markdown documents; {len(errors)} errors.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())

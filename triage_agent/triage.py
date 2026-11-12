"""Local entry point for the same deterministic pipeline deployed in AMS."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "plugins" / "alert_triage"))
from triage import main

if __name__ == "__main__":
    raise SystemExit(main())

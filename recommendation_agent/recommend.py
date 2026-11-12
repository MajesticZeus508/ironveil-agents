"""Local CLI; live mode requires approved SDK/gateway configuration."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
from ams.core import ArgonClient, LIMIT, ValidationError, parse, recommend, render_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        targets = [args.output_dir / name for name in ("recommendation_results.json", "recommendation_report.md")]
        if any(p.exists() or p.resolve() == args.input.resolve() for p in targets):
            raise ValidationError("output_already_exists")
        with args.input.open("rb") as stream:
            data, digest = parse(stream.read(LIMIT + 1))
        import os
        if not os.getenv("LITELLM_PROXY_BASE_URL"):
            raise ValidationError("missing_gateway_configuration")
        try:
            import spark_agent_kit
            import sling_agent
        except ImportError:
            raise ValidationError("missing_sdk_dependency") from None
        result = asyncio.run(recommend(data, ArgonClient(), digest))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for path, content in zip(targets, (json.dumps(result, indent=2, allow_nan=False), render_report(result))):
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
        print(f"{result['run']['status']}: {result['run']['completed']}/{result['run']['incident_count']} analyses completed")
        return 0 if result["run"]["status"] == "completed" else 2
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError:
        print("File access failed; check input/output paths and permissions.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

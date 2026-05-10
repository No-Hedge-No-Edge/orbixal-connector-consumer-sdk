"""Sync generated Consumer SDK models from the canonical platform schemas."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


SDK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLATFORM_ROOT = SDK_ROOT.parents[1] / "orbixal-data-connector"
GENERATED_DIR = SDK_ROOT / "src" / "connector_consumer_sdk" / "generated"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--platform-root",
        default=os.getenv("ORBIXAL_DATA_CONNECTOR_ROOT", str(DEFAULT_PLATFORM_ROOT)),
    )
    parser.add_argument("--check", action="store_true", help="Fail if generated models change.")
    args = parser.parse_args()
    platform_root = Path(args.platform_root).expanduser().resolve()
    generator = platform_root / "scripts" / "generate_models.py"
    if not generator.is_file():
        raise SystemExit(f"Canonical model generator not found: {generator}")

    before = _snapshot_generated_files()
    env = dict(os.environ)
    env["CONSUMER_SDK_GENERATED_DIR"] = str(GENERATED_DIR)
    subprocess.run([sys.executable, str(generator)], cwd=platform_root, env=env, check=True)
    after = _snapshot_generated_files()
    if args.check and before != after:
        changed = sorted(set(before) | set(after))
        changed = [path for path in changed if before.get(path) != after.get(path)]
        raise SystemExit(
            "Generated Consumer SDK models are out of sync: " + ", ".join(changed)
        )


def _snapshot_generated_files() -> dict[str, str]:
    if not GENERATED_DIR.exists():
        return {}
    return {
        str(path.relative_to(GENERATED_DIR)): path.read_text(encoding="utf-8")
        for path in sorted(GENERATED_DIR.glob("*.py"))
    }


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""CLI for building/checking the v2 synthetic-silver anchor manifest.

Usage:
    python scripts/bernie_synthetic_silver_v2_anchors.py --write
    python scripts/bernie_synthetic_silver_v2_anchors.py --check
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.synthetic_noise_v2 import (  # noqa: E402
    DEFAULT_SEED_PATH_V2,
    check_v2_anchor_manifest,
    write_v2_anchor_manifest,
)


def main() -> int:
    args = set(sys.argv[1:])

    if "--write" in args:
        manifest = write_v2_anchor_manifest()
        print(
            f"Written {manifest['anchor_count']} anchors "
            f"to {DEFAULT_SEED_PATH_V2}"
        )
        print(f"Manifest hash: {manifest['manifest_hash']}")
        return 0

    if "--check" in args:
        errors = check_v2_anchor_manifest()
        if errors:
            print(
                f"CHECK FAILED: {len(errors)} error(s):", file=sys.stderr
            )
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print(f"CHECK PASSED: {DEFAULT_SEED_PATH_V2} is valid")
        return 0

    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

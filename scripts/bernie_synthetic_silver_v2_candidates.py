"""Generate or verify the coherent synthetic Silver v2 candidate artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.synthetic_noise_v2_candidates import (  # noqa: E402
    DEFAULT_ADMISSION_PATH_V2,
    DEFAULT_CANDIDATE_PATH_V2,
    build_v2_candidate_artifacts,
    check_v2_candidate_artifacts,
    write_json,
    write_jsonl,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        manifest, records, admission = build_v2_candidate_artifacts()
        write_jsonl(DEFAULT_CANDIDATE_PATH_V2, records)
        write_json(DEFAULT_ADMISSION_PATH_V2, admission)
        print(f"wrote {len(records)} candidates from {manifest['anchor_count']} anchors")
        print(f"CANDIDATE_HASH: {admission['canonical_candidate_hash']}")
        print(f"ADMISSION_HASH: {admission['admission_hash']}")
        return 0
    errors = check_v2_candidate_artifacts()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("validated 192 coherent v2 candidates and exact admission")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

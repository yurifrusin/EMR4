"""Sol-owned mechanical validator for one noisy-dialogue model lane."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.bernie.synthetic_noise_corpus import (  # noqa: E402
    DEFAULT_SEED_PATH,
    candidate_records_hash,
    load_jsonl,
    validate_candidate_records,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--provider-id", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--lane-id", required=True)
    parser.add_argument("--candidate-prefix", required=True)
    parser.add_argument("--seed-manifest", type=Path, default=DEFAULT_SEED_PATH)
    args = parser.parse_args()

    seeds = json.loads(args.seed_manifest.read_text(encoding="utf-8"))
    records = load_jsonl(args.input)
    errors = validate_candidate_records(
        records,
        seeds,
        expected_generator_identity={
            "provider_id": args.provider_id,
            "model_id": args.model_id,
            "lane_id": args.lane_id,
        },
        candidate_prefix=args.candidate_prefix,
    )
    if errors:
        for error in errors:
            print(error)
        print(f"revision_required: {len(errors)} mechanical error(s)")
        return 1
    print(
        f"pass: {len(records)} candidates; "
        f"hash={candidate_records_hash(records)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

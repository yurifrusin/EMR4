"""Build or check the development-only noisy-dialogue semantic seed manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.services.bernie.synthetic_noise_corpus import (
    DEFAULT_SEED_PATH,
    build_semantic_seed_manifest,
    validate_semantic_seed_manifest,
    write_semantic_seed_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_SEED_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = build_semantic_seed_manifest()
    if args.check:
        if not args.output.is_file():
            raise SystemExit(f"missing seed manifest: {args.output}")
        actual = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate_semantic_seed_manifest(actual)
        if actual != expected:
            errors.append("seed manifest is not byte-semantic identical to regeneration")
        if errors:
            raise SystemExit("; ".join(errors))
        print(f"pass: {args.output} ({actual['seed_count']} seeds)")
        return 0

    manifest = write_semantic_seed_manifest(args.output)
    print(f"wrote: {args.output} ({manifest['seed_count']} seeds)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

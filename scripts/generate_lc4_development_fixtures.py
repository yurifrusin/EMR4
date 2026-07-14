"""Generate all 96 LC4 development group fixture files deterministically.

Usage:
    python scripts/generate_lc4_development_fixtures.py

Output:
    tests/fixtures/bernie_lc4_development/
        96 group JSON files + lc4_development_manifest.json
"""

from __future__ import annotations

import pathlib
import sys

# Ensure app is importable
_HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

from app.services.bernie.scale_corpus import generate_development_fixture, validate_corpus


def main() -> None:
    output_dir = _HERE / "tests" / "fixtures" / "bernie_lc4_development"
    print(f"Generating 96 development groups into {output_dir}...")

    corpus = generate_development_fixture(output_dir)

    # Validate
    errors = validate_corpus(corpus)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    total_variants = sum(len(g.surface_variants) + len(g.multi_turn_variants) for g in corpus.groups)
    mt_variants = sum(len(g.multi_turn_variants) for g in corpus.groups)
    print(f"Generated {len(corpus.groups)} groups")
    print(f"  Total variants: {total_variants} ({total_variants - mt_variants} surface + {mt_variants} MT)")
    print(f"  Gap-priority groups: {corpus.gap_priority_group_count}")

    # Print coverage stats
    from collections import Counter
    actions = Counter(g.spec.intended_action for g in corpus.groups)
    temporals = Counter(g.spec.temporal_relation for g in corpus.groups)
    print(f"\nAction coverage: {dict(actions)}")
    print(f"Temporal coverage: {dict(temporals)}")
    print("Done.")


if __name__ == "__main__":
    main()

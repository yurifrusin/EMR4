"""Launch the exact-digest historical-derived check-in adapter-test consumer."""

from __future__ import annotations

import sys
from pathlib import Path


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration_harness.historical_diary_check_in_adapter_test_consumption import (  # noqa: E402
    main,
)


if __name__ == "__main__":
    raise SystemExit(main())

"""Selected production-helper unit contract for appointment capacity math.

This is a NEW math-only unit contract, not before/after CREATE repair proof.
It does not import the application, FastAPI, models, settings, or providers.
The exception and status doubles below describe only the math refusal shape.
SQL compilation, real database locks, transaction rollback, completed replay,
and actual CREATE caller regression checks require separate admitted tests.

Normal development: run this file from the repository tests directory.
An isolated finite binding may supply --source and an exact --tz-root.
Missing source, helpers, or timezone data is a failure; nothing is skipped.
"""

import argparse
import ast
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import sys
import typing
import unittest
import zoneinfo


_SOURCE_PATH = Path(__file__).resolve().parents[1] / "app" / "routers" / "appointments.py"
_PURE_DEFINITIONS = (
    "_AppointmentCapacityRefusal",
    "_appointment_capacity_zone",
    "_appointment_capacity_wall_instant",
    "_appointment_capacity_window",
    "_appointment_capacity_starts",
    "_appointment_capacity_interval",
)


class _MathOnlyHTTPException(Exception):
    """Dependency double only; this does not verify FastAPI integration."""

    def __init__(self, *, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class _MathOnlyStatus:
    HTTP_409_CONFLICT = 409


def _load_selected_math(source_path):
    """Parse source, then execute only the six exact top-level definitions."""
    source_text = source_path.read_text(encoding="utf-8")
    source_tree = ast.parse(source_text, filename=str(source_path))
    definitions = {}
    for node in source_tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in _PURE_DEFINITIONS:
                if node.name in definitions:
                    raise AssertionError("Duplicate selected definition: " + node.name)
                definitions[node.name] = node
    if set(definitions) != set(_PURE_DEFINITIONS):
        raise AssertionError(
            "Missing selected production definitions: "
            + repr(sorted(set(_PURE_DEFINITIONS) - set(definitions)))
        )
    selected = []
    for name in _PURE_DEFINITIONS:
        node = definitions[name]
        expected_type = ast.ClassDef if name == "_AppointmentCapacityRefusal" else ast.FunctionDef
        if type(node) is not expected_type or node.decorator_list:
            raise AssertionError("Unexpected selected definition shape: " + name)
        if any(isinstance(part, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal))
               for part in ast.walk(node)):
            raise AssertionError("Non-pure statement in selected definition: " + name)
        selected.append(node)

    # No application imports, source globals, or other source helpers are loaded.
    # The restricted builtins deliberately omit import, open, eval, and exec.
    namespace = {
        "__name__": "selected_appointment_capacity_math",
        "__builtins__": {
            "__build_class__": __build_class__,
            "super": super,
            "isinstance": isinstance,
            "type": type,
            "str": str,
            "int": int,
            "bool": bool,
            "tuple": tuple,
            "list": list,
            "set": set,
            "range": range,
            "len": len,
            "OverflowError": OverflowError,
            "ValueError": ValueError,
        },
        "HTTPException": _MathOnlyHTTPException,
        "status": _MathOnlyStatus,
        "Any": typing.Any,
        "Literal": typing.Literal,
        "Optional": typing.Optional,
        "date_type": date,
        "datetime": datetime,
        "time": time,
        "timedelta": timedelta,
        "timezone": timezone,
        "ZoneInfo": zoneinfo.ZoneInfo,
        "ZoneInfoNotFoundError": zoneinfo.ZoneInfoNotFoundError,
    }
    selected_module = ast.Module(body=selected, type_ignores=[])
    selected_code = compile(selected_module, str(source_path), "exec", dont_inherit=True)
    exec(selected_code, namespace, namespace)
    return namespace


class AppointmentCreateCapacityMathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.math = _load_selected_math(_SOURCE_PATH)
        cls.sydney = cls.math["_appointment_capacity_zone"]("Australia/Sydney")

    def assert_refusal(self, reason, function, *args, **kwargs):
        with self.assertRaises(self.math["_AppointmentCapacityRefusal"]) as caught:
            function(*args, **kwargs)
        error = caught.exception
        self.assertEqual(error.status_code, 409)
        self.assertEqual(error.detail["code"], "appointment_capacity_unavailable")
        self.assertEqual(error.detail["reason"], reason)

    def assert_interval(self, target_date, start, duration, schedule, expected,
                        *, canonical_start=None):
        actual = self.math["_appointment_capacity_interval"](
            target_date, start, duration, schedule, self.sydney,
            canonical_start=canonical_start,
        )
        if expected is None:
            self.assertIsNone(actual)
        else:
            self.assertEqual(
                actual,
                tuple(datetime.fromisoformat(value) for value in expected),
            )

    def test_strict_zoneinfo_has_no_default_timezone_fallback(self):
        zone = self.math["_appointment_capacity_zone"]
        self.assertEqual(zone("Australia/Sydney").key, "Australia/Sydney")
        for value in (None, "", 123, "Not/A_Real_Zone"):
            with self.subTest(value=value):
                self.assert_refusal("invalid_timezone", zone, value)

    def test_effective_window_start_grid_and_elapsed_duration(self):
        target = date(2026, 11, 9)
        schedule = (time(9), time(12, 30), 30)
        cases = (
            ("twenty_minutes_is_valid", time(9), 20,
             ("2026-11-08T22:00:00+00:00", "2026-11-08T22:20:00+00:00")),
            ("exact_end_is_valid", time(12), 30,
             ("2026-11-09T01:00:00+00:00", "2026-11-09T01:30:00+00:00")),
            ("off_grid", time(9, 15), 15, None),
            ("before_window", time(8, 59), 20, None),
            ("start_at_end", time(12, 30), 1, None),
            ("full_interval_overrun", time(12), 31, None),
        )
        for label, start, duration, expected in cases:
            with self.subTest(case=label):
                self.assert_interval(target, start, duration, schedule, expected)
        non_round = (time(9, 10), time(12, 40), 30)
        self.assert_interval(
            target, time(9, 40), 20, non_round,
            ("2026-11-08T22:40:00+00:00", "2026-11-08T23:00:00+00:00"),
        )
        self.assert_interval(target, time(9, 30), 20, non_round, None)

    def test_malformed_calendar_and_grid_refuse(self):
        window = self.math["_appointment_capacity_window"]
        target = date(2026, 11, 9)
        bad_schedules = (
            (time(9), time(9), 30),
            (time(22), time(2), 30),
            (time(9, tzinfo=timezone.utc), time(12), 30),
            (time(9), time(12), 0),
            (time(9), time(12), -1),
            (time(9), time(12), True),
            (time(9), time(12), 1.5),
            (time(9), time(12), 10 ** 30),
        )
        for schedule in bad_schedules:
            with self.subTest(schedule=schedule):
                self.assert_refusal("malformed_calendar", window, target, schedule, self.sydney)

    def test_positive_duration_and_aware_private_canonical_argument(self):
        interval = self.math["_appointment_capacity_interval"]
        target = date(2026, 11, 9)
        schedule = (time(9), time(12, 30), 30)
        for duration in (0, -1, True, 1.5):
            with self.subTest(duration=duration):
                self.assert_refusal(
                    "malformed_calendar", interval,
                    target, time(9), duration, schedule, self.sydney,
                )
        self.assert_refusal(
            "invalid_local_boundary", interval,
            target, time(9, tzinfo=timezone.utc), 20, schedule, self.sydney,
        )
        self.assert_refusal(
            "invalid_local_boundary", interval,
            target, time(9), 20, schedule, self.sydney,
            canonical_start=datetime(2026, 11, 9, 9),
        )
        self.assert_interval(
            target, time(9), 20, schedule, None,
            canonical_start=datetime.fromisoformat("2026-11-09T09:00:00+10:00"),
        )

    def test_valid_grid_larger_than_day_has_one_finite_start(self):
        target = date(2026, 11, 9)
        schedule = (time(9), time(12, 30), 1_000_000_000)
        self.math["_appointment_capacity_window"](target, schedule, self.sydney)
        self.assertEqual(
            self.math["_appointment_capacity_starts"](target, schedule),
            [datetime(2026, 11, 9, 9)],
        )
        self.assert_interval(
            target, time(9), 20, schedule,
            ("2026-11-08T22:00:00+00:00", "2026-11-08T22:20:00+00:00"),
        )

    def test_generated_sydney_gap_and_fold_boundaries_refuse(self):
        wall_instant = self.math["_appointment_capacity_wall_instant"]
        window = self.math["_appointment_capacity_window"]
        interval = self.math["_appointment_capacity_interval"]
        for target in (date(2026, 10, 4), date(2026, 4, 5)):
            with self.subTest(date=target):
                self.assert_refusal(
                    "invalid_local_boundary", wall_instant,
                    datetime.combine(target, time(2, 30)), self.sydney,
                )
                self.assert_refusal(
                    "invalid_local_boundary", window,
                    target, (time(2, 30), time(4), 30), self.sydney,
                )
                self.assert_refusal(
                    "invalid_local_boundary", window,
                    target, (time(1), time(2, 30), 30), self.sydney,
                )
                self.assert_refusal(
                    "invalid_local_boundary", interval,
                    target, time(2, 30), 20, (time(1), time(4), 30), self.sydney,
                )
        # A unique generated start whose generated end is in the fold also closes.
        self.assert_refusal(
            "invalid_local_boundary", interval,
            date(2026, 4, 5), time(1, 30), 60,
            (time(1), time(4), 30), self.sydney,
        )

    def test_supplied_fold_instants_and_elapsed_gap_crossing_remain_valid(self):
        # These supplied instants are oracles, not a replacement canonicalizer.
        target = date(2026, 4, 5)
        schedule = (time(1), time(4), 30)
        cases = (
            ("2026-04-05T02:30:00+11:00",
             ("2026-04-04T15:30:00+00:00", "2026-04-04T15:50:00+00:00")),
            ("2026-04-05T02:30:00+10:00",
             ("2026-04-04T16:30:00+00:00", "2026-04-04T16:50:00+00:00")),
        )
        for supplied, expected in cases:
            with self.subTest(canonical_start=supplied):
                self.assert_interval(
                    target, time(2, 30), 20, schedule, expected,
                    canonical_start=datetime.fromisoformat(supplied),
                )
        # Two elapsed hours cross three wall-clock hours at the spring transition.
        self.assert_interval(
            date(2026, 10, 4), time(1), 120, (time(1), time(4), 30),
            ("2026-10-03T15:00:00+00:00", "2026-10-03T17:00:00+00:00"),
        )


def main(argv=None):
    global _SOURCE_PATH
    parser = argparse.ArgumentParser(
        description="Math-only selected appointment-capacity helper contract.",
    )
    parser.add_argument("--source", type=Path, default=_SOURCE_PATH)
    parser.add_argument("--tz-root", type=Path)
    options, unittest_args = parser.parse_known_args(argv)
    _SOURCE_PATH = options.source.resolve()
    if options.tz_root is not None:
        tz_root = options.tz_root.resolve(strict=True)
        if not tz_root.is_dir():
            parser.error("--tz-root must identify the admitted timezone-data directory")
        zoneinfo.reset_tzpath((str(tz_root),))
        zoneinfo.ZoneInfo.clear_cache()
    unittest.main(argv=[sys.argv[0], *unittest_args], verbosity=2)


if __name__ == "__main__":
    main()

"""Bounded-domain home for Bernie temporal interpretation policy.

This module is the designated single home for Bernie's temporal policy. Today
it publishes the pure natural-language time/date helpers that currently live
(with private names) inside the legacy interpreter module; a later sprint
migrates the remaining duplicated temporal logic here:

- the same-day clamp / clinic-day-exhaustion policy, currently implemented
  twice inside ``app/routers/appointments.py`` (interpret path and supervised
  wrapper);
- the week-relative phrase handling duplicated between the interpreter service
  and the router.

All functions here are pure: no DB, no network, no wall-clock. The
business-hours assumption (bare hour 1-11 without am/pm is treated as pm) is
documented on ``parse_time_fragment``; surfacing it as an explicit
``BernieAssumption`` is later-sprint work.
"""

from app.services.bernie_booking_interpreter import (
    _extract_natural_date_constraint,
    _extract_natural_time_constraints,
    _parse_time_fragment,
)

# Public bounded-domain names for the pure temporal helpers. These are
# identity re-exports - behaviour is exactly the legacy interpreter's.
parse_time_fragment = _parse_time_fragment
extract_natural_time_constraints = _extract_natural_time_constraints
extract_natural_date_constraint = _extract_natural_date_constraint

__all__ = [
    "parse_time_fragment",
    "extract_natural_time_constraints",
    "extract_natural_date_constraint",
]

# Status confirmation now works against a real disposable PostgreSQL database

Date: 2026-08-13

Timestamp: 2026-08-13T11:39:46+10:00 (Australia/Brisbane)

Both the application adapter and its database behavior now pass together.
This is the last major hidden-infrastructure join before we can safely converge
the existing HTTP route and then return to visible Diary UI work.

The important practical results are:

- the database tenant boundary is set before any appointment, staff, audit or
  receipt access;
- staff authority is checked twice against current database truth;
- one confirmation produces exactly one appointment change, one attributable
  audit and one complete replay receipt;
- if the response is lost, retry returns the exact stored answer without
  changing the appointment again;
- stale proposals, revoked staff, wrong roles, cross-practice access and broken
  response projection all stop safely; and
- every disposable database/container/network was removed and its absence
  proved.

The database exposed a subtle real-world type mismatch: JSON carried the
appointment identity as text while PostgreSQL returned a UUID, so an exact
retry looked different. That is now normalized at the narrow boundary without
changing what was signed or admitted.

No real practice, patient or product data was used. No provider call, live
route, deployment or production system was touched.

Next, the existing authenticated status-confirm route can be converged onto
this proved path and rehearsed locally with synthetic data. Once that route
tranche passes, visible Diary UI integration becomes the immediate horizon.

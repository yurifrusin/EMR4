# Ariadne agent error and correction register — revision 321

Date: 2026-08-17

Timestamp: 2026-08-17T07:21:22.2389208+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 321 records 370 bounded known incidents. No incident is open.

- AER-0369 preserves and corrects the delete-confirm route/adapter
  canonicalization and fresh-command-session RLS-context repository defect.
- AER-0370 preserves another stopped recurrence of manually expanding a short
  displayed Git prefix into a nonexistent full object ID. Direct `git
  rev-parse HEAD` exposed the mismatch before preflight, staging or commit.
  The corrected runtime uses exact machine output and must pass the existing
  commit-resolution preflight.

The Git recurrence is workflow evidence, not a product defect. The product
candidate, database state and protected refs remained unchanged by it. No
provider call, protected evidence access, database run, deployment, release or
Pages action occurred.

# Sol acceptance: Context Fabric durability parse formatting recovery

Date: 2026-08-10

Accepted candidate: `e5a51232a7d1c503e772e8467f7241d971c184b7`

The first exact-evidence veto at `58538b3b` correctly returned
`revision_required` because two tests were not in canonical Ruff format. No
database run followed. The replacement mechanically reformatted those tests and
preserved the rejected receipt.

Fresh r152 Gemini 3.6 Flash/high review passed at the exact replacement HEAD
with a clean postcondition. It independently passed 462/462 tests, twelve-file
Ruff lint and formatting, the architecture builder, inert rehearsal, exact
parent resolution, digest and evidence-path reconciliation, and both diff
checks. It correctly distinguished the mutable generic characterization target
from the immutable admission-row-shape fixture and the protected historical
failure target.

This accepts the candidate for one fixed-path, networkless, pull-never,
tmpfs-only disposable PostgreSQL 16 exact reproduction after fresh preexecution
rehydration, protected-evidence backup and exact local image inspection. It
does not accept behavior execution, an applied migration, operational database,
listener/feed, patient/product/clinical data, app/API/Diary command, deployment,
Pages, production, release or protected-ref movement.

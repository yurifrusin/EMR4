# Ariadne agent error and correction register — revision 203

Date: 2026-08-08

Revision 203 adds AER-0237 and brings the register to 237 bounded incidents.

## AER-0237 — rollback fixture skipped the first contiguous position

Behavior attempt 047 reached BTR-B03 expecting the fixed injected rollback
SQLSTATE `P0001` but observed `22012`. Repository-only diagnosis proved that
the rollback observer remained at checkpoint zero while the fixture admitted
and transitioned source position two. The artifact correctly classified that
as a coverage gap and returned `REBASE_APPLIED`; the harness's typed
`RECEIPT_APPLIED` assertion then divided by zero before the intended injection.

The correction uses already available source position one for the rollback
observer's precommitted primary, transition and retention probe. That is the
first contiguous position and therefore exercises the original contract: an
otherwise applicable transition whose effects must all roll back on fixed
`P0001`. Generated SQL, parse evidence, the twenty-scenario contract and all
authority boundaries remain unchanged.

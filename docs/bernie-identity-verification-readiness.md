# Bernie Identity Verification Readiness

Sprint 95 prepares EMR4 for non-mutating identity checks that can support Bernie
booking proposals without turning Caller ID, LLM output, or a selected diary slot
into proof of identity.

## Contract

Identity verification runs through `app/services/identity_verification.py`.

The default adapter is disabled and fails closed. It performs no network access.

The provider-neutral result is intentionally small:

- `method`: `opv`, `pvm`, `pvf`, `ovv`, or `ihi`
- `status`: verified, not verified, needs more information, unavailable, or disabled
- `verified`: boolean
- `reason_code`: compact machine-readable reason
- `matched_fields`: field names only, not raw returned data
- `warnings`: compact warning codes
- `raw_response_stored`: defaults to false

The result can be converted into an `identity_verification` context frame for
Bernie staff-review payloads. Bernie may use that frame as supporting evidence,
but the final booking write remains staff-confirmed.

## Caller ID

Caller ID is supporting context, not verified identity. A phone-number match can
raise confidence when it matches a linked patient record, but staff should still
confirm DOB and use Medicare/card or other identifiers when uncertainty remains.

## OPV/PVM Boundary

Medicare Online / OPV / PVM integration should be added behind the adapter only
after the exact provider contract, credentials, consent posture, logging policy,
and error semantics are reviewed.

Do not put live OPV/PVM calls inside Bernie prompt code or Diary UI code.

## ONLYNAME

ONLYNAME handling remains a verification item. EMR4 should not canonicalise
one-name Medicare claim mapping until the exact Medicare Online / Services
Australia contract used by the implementation is confirmed.


# Ariadne agent error and correction register revision 111

Date: 2026-08-08

Status: accepted register correction

Revision 111 adds AER-0134 and brings the register to 134 bounded incidents.

## AER-0134 - behavior isolation contradicted the parent entry point

Attempt 012 identified scenario `BTR-E01` and SQLSTATE `CF303`. The accepted
generation-registration function explicitly requires a serializable top-level
transaction, while the later behavior plan and renderer had flattened every
scenario to read committed.

The accepted SQL remains unchanged. Registration and coordinator
apply/replay/rollback scenarios now use serializable transactions; producer,
observer, trigger and RLS scenarios retain read committed. Contract, renderer
and evidence tests bind that exact four-scenario set. Another run remains
ineligible pending deterministic checks and a fresh exact-HEAD veto.
